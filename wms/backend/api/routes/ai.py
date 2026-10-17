"""
AI features (Claude API):
  • scan-invoice  — read a supplier invoice / delivery note (photo or PDF) into lines,
                    matched to your products, ready to become a purchase order
  • chat          — "ask your data": answers questions using read-only tools over the
                    business's sales, customers, stock and forecasts
  • draft-message — a short re-engagement message for a customer who stopped buying
"""
import base64
import difflib
import json
import unicodedata
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from typing import Literal, Optional

import anthropic
from anthropic import beta_tool
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from core.config import AI_MODEL
from core.security import get_current_user
from db.supabase_client import supabase
from services import ai
from services.forecasting import detect_anomalies, plan_reorders, plan_to_dict
from services.permissions import check_business_access

router = APIRouter(prefix="/api/ai", tags=["AI"])

MAX_FILE_BYTES = 10 * 1024 * 1024
IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


@router.get("/status")
def status(business_id: str, user_id: str = Depends(get_current_user)):
    check_business_access(user_id, business_id)
    return {"enabled": ai.enabled(), "model": AI_MODEL,
            "remaining_today": ai.remaining_today(business_id) if ai.enabled() else 0}


# ── Invoice / delivery note scanning ──────────────────────────────────────────

class InvoiceLine(BaseModel):
    description: str = Field(description="Product description exactly as printed")
    code: Optional[str] = Field(description="Supplier's product code / SKU on the line, if any")
    barcode: Optional[str] = Field(description="EAN/UPC barcode on the line, if any")
    quantity: float = Field(description="Quantity delivered/invoiced, in the unit printed")
    unit: Optional[str] = Field(description="Unit as printed, e.g. τεμ, κιβ, kg")
    unit_price: Optional[float] = Field(description="Net price per unit before VAT, if printed")
    line_total: Optional[float] = Field(description="Net line total before VAT, if printed")


class InvoiceExtraction(BaseModel):
    document_type: Literal["invoice", "delivery_note", "receipt", "other"]
    supplier_name: Optional[str]
    document_number: Optional[str]
    document_date: Optional[str] = Field(description="YYYY-MM-DD")
    currency: Optional[str]
    lines: list[InvoiceLine]
    warnings: list[str] = Field(description="Anything unreadable or ambiguous, in the user's language")


INVOICE_PROMPT = """Extract the product lines from this supplier document (invoice, delivery note or receipt).

Rules:
- One entry per product line. Skip shipping, discounts, VAT summary and payment rows.
- Copy description and codes exactly as printed; do not translate or normalise them.
- Numbers use the document's decimal convention (Greek documents use a comma for decimals and a dot for thousands) — return them as plain numbers.
- unit_price is the net unit price before VAT. Leave a field null if it isn't printed; never guess.
- If something is unreadable or ambiguous, still return the line with your best reading and add a short warning.
Write warnings in {language}."""


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in s if not unicodedata.combining(c) and (c.isalnum() or c == " ")).strip()


def _match(lines: list[InvoiceLine], products: list[dict]) -> list[dict]:
    by_sku = {p["sku"].strip().lower(): p for p in products}
    by_barcode = {p["barcode"].strip(): p for p in products if p.get("barcode")}
    names = {p["id"]: _norm(p["name"]) for p in products}
    out = []
    for line in lines:
        match, how = None, None
        for code in (line.barcode, line.code):
            if code and code.strip() in by_barcode:
                match, how = by_barcode[code.strip()], "barcode"
                break
            if code and code.strip().lower() in by_sku:
                match, how = by_sku[code.strip().lower()], "sku"
                break
        score = 1.0 if match else 0.0
        if not match and products:
            target = _norm(line.description)
            best = max(products, key=lambda p: difflib.SequenceMatcher(None, target, names[p["id"]]).ratio())
            score = difflib.SequenceMatcher(None, target, names[best["id"]]).ratio()
            if score >= 0.55:
                match, how = best, "name"
        out.append({
            **line.model_dump(),
            "match": {"product_id": match["id"], "sku": match["sku"], "name": match["name"],
                      "by": how, "score": round(score, 2)} if match else None,
        })
    return out


@router.post("/scan-invoice")
async def scan_invoice(
    business_id: str = Form(...),
    language: str = Form("el"),
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user),
):
    check_business_access(user_id, business_id)
    data = await file.read(MAX_FILE_BYTES + 1)
    if len(data) > MAX_FILE_BYTES:
        raise HTTPException(413, "File too large (max 10 MB)")
    media_type = (file.content_type or "").lower()
    if media_type == "application/pdf":
        doc = {"type": "document", "source": {"type": "base64", "media_type": "application/pdf",
                                              "data": base64.standard_b64encode(data).decode()}}
    elif media_type in IMAGE_TYPES:
        doc = {"type": "image", "source": {"type": "base64", "media_type": media_type,
                                           "data": base64.standard_b64encode(data).decode()}}
    else:
        raise HTTPException(400, "Upload a photo (JPG, PNG, WEBP) or a PDF")

    ai.consume_quota(business_id, "scan_invoice")
    try:
        response = ai.client().beta.messages.parse(
            **ai.request_options(),
            max_tokens=16000,
            output_config={"effort": "medium"},
            output_format=InvoiceExtraction,
            messages=[{"role": "user", "content": [
                doc,
                {"type": "text", "text": INVOICE_PROMPT.format(language="Greek" if language == "el" else "English")},
            ]}],
        )
    except anthropic.APIError as e:
        ai.raise_for_api_error(e)
    if response.stop_reason == "refusal" or response.parsed_output is None:
        raise HTTPException(422, "Could not read this document")

    extraction: InvoiceExtraction = response.parsed_output
    products = supabase.table("products").select("id, sku, name, barcode, supplier, cost_price") \
        .eq("business_id", business_id).execute().data or []
    return {**extraction.model_dump(exclude={"lines"}), "lines": _match(extraction.lines, products)}


# ── Ask your data ─────────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    business_id: str
    messages: list[ChatMessage] = Field(min_length=1, max_length=30)
    language: Literal["el", "en"] = "el"


def _parse_day(s: str) -> date:
    try:
        return date.fromisoformat(s[:10])
    except ValueError:
        raise ValueError(f"Invalid date {s!r}, use YYYY-MM-DD")


def _sales_lines(business_id: str, start: date, end: date) -> list[dict]:
    """Completed sale order lines in [start, end], with order date and customer."""
    orders = supabase.table("orders").select("id, party_name, created_at") \
        .eq("business_id", business_id).eq("type", "sale").eq("status", "completed") \
        .gte("created_at", start.isoformat()).lt("created_at", (end + timedelta(days=1)).isoformat()) \
        .limit(20000).execute().data or []
    if not orders:
        return []
    meta = {o["id"]: o for o in orders}
    items = []
    ids = list(meta)
    for i in range(0, len(ids), 300):
        items += supabase.table("order_items").select("order_id, quantity, unit_price, products(sku, name)") \
            .in_("order_id", ids[i:i + 300]).execute().data or []
    return [{**it, "customer": meta[it["order_id"]]["party_name"] or "—",
             "day": meta[it["order_id"]]["created_at"][:10]} for it in items]


def _build_tools(business_id: str):
    @beta_tool
    def sales_summary(start_date: str, end_date: str, group_by: str = "product", limit: int = 20) -> str:
        """Revenue, units and order count from completed sales between two dates (inclusive).

        Args:
            start_date: First day, YYYY-MM-DD.
            end_date: Last day, YYYY-MM-DD.
            group_by: One of "product", "customer", "day", "month", "total".
            limit: Max rows to return (sorted by revenue, highest first).
        """
        lines = _sales_lines(business_id, _parse_day(start_date), _parse_day(end_date))
        groups: dict[str, dict] = defaultdict(lambda: {"revenue": 0.0, "units": 0, "orders": set()})
        for l in lines:
            key = {"product": f"{(l.get('products') or {}).get('name')} ({(l.get('products') or {}).get('sku')})",
                   "customer": l["customer"], "day": l["day"], "month": l["day"][:7]}.get(group_by, "total")
            g = groups[key]
            g["revenue"] += l["quantity"] * (l["unit_price"] or 0)
            g["units"] += l["quantity"]
            g["orders"].add(l["order_id"])
        rows = [{"group": k, "revenue": round(v["revenue"], 2), "units": v["units"], "orders": len(v["orders"])}
                for k, v in groups.items()]
        rows.sort(key=lambda r: r["group"] if group_by in ("day", "month") else -r["revenue"])
        return json.dumps({"rows": rows[:max(1, min(limit, 100))], "total_groups": len(rows)}, ensure_ascii=False)

    @beta_tool
    def customer_trends(period_days: int = 90) -> str:
        """Compare each customer's revenue in the last `period_days` with the period before it.
        Use for questions like "who is buying less / more" or "which customers stopped ordering".

        Args:
            period_days: Length of each period in days (e.g. 30, 90).
        """
        today = datetime.now(timezone.utc).date()
        period_days = max(7, min(period_days, 365))
        lines = _sales_lines(business_id, today - timedelta(days=2 * period_days), today)
        cur: dict[str, float] = defaultdict(float)
        prev: dict[str, float] = defaultdict(float)
        last: dict[str, str] = {}
        for l in lines:
            value = l["quantity"] * (l["unit_price"] or 0)
            age = (today - date.fromisoformat(l["day"])).days
            (cur if age < period_days else prev)[l["customer"]] += value
            last[l["customer"]] = max(last.get(l["customer"], ""), l["day"])
        rows = []
        for c in set(cur) | set(prev):
            change = None if prev[c] == 0 else round((cur[c] - prev[c]) / prev[c] * 100, 1)
            rows.append({"customer": c, "current": round(cur[c], 2), "previous": round(prev[c], 2),
                         "change_pct": change, "last_order": last.get(c)})
        rows.sort(key=lambda r: (r["change_pct"] is None, r["change_pct"] or 0))
        return json.dumps({"period_days": period_days, "customers": rows[:60]}, ensure_ascii=False)

    @beta_tool
    def stock_status(search: str = "", only_needing_reorder: bool = False) -> str:
        """Current stock per product with forecast demand, days until it runs out and the
        suggested order quantity.

        Args:
            search: Optional text to filter by product name or SKU.
            only_needing_reorder: If true, return only products that should be reordered soon.
        """
        plans = [plan_to_dict(p) for p in plan_reorders(business_id)]
        if search:
            s = search.lower()
            plans = [p for p in plans if s in p["name"].lower() or s in p["sku"].lower()]
        if only_needing_reorder:
            plans = [p for p in plans if p["urgency"] != "ok"]
        keep = ("sku", "name", "current_stock", "on_order", "reorder_point", "avg_daily", "forecast_30",
                "days_until_stockout", "suggested_qty", "reorder_by", "urgency", "supplier")
        return json.dumps([{k: p[k] for k in keep} for p in plans[:80]], ensure_ascii=False)

    @beta_tool
    def recent_orders(order_type: str = "", status: str = "", limit: int = 20) -> str:
        """Most recent orders with their totals.

        Args:
            order_type: "sale", "purchase" or "" for both.
            status: "draft", "confirmed", "completed", "cancelled" or "" for all.
            limit: Max orders to return.
        """
        q = supabase.table("orders").select("id, type, status, party_name, created_at, order_items(quantity, unit_price)") \
            .eq("business_id", business_id).order("created_at", desc=True).limit(max(1, min(limit, 50)))
        if order_type:
            q = q.eq("type", order_type)
        if status:
            q = q.eq("status", status)
        rows = [{"type": o["type"], "status": o["status"], "party": o["party_name"], "date": o["created_at"][:10],
                 "total": round(sum(i["quantity"] * (i["unit_price"] or 0) for i in o.get("order_items") or []), 2)}
                for o in q.execute().data or []]
        return json.dumps(rows, ensure_ascii=False)

    @beta_tool
    def unusual_activity() -> str:
        """Products with sudden sales drops or spikes, stock lost in recounts, and weekly revenue drops."""
        return json.dumps(detect_anomalies(business_id), ensure_ascii=False)

    return [sales_summary, customer_trends, stock_status, recent_orders, unusual_activity]


CHAT_SYSTEM = """You are the assistant inside WMS, a warehouse and sales app, helping the team of "{business}".
Today is {today}. Currency is euro (€).

Answer questions about this business using the tools; they read live data. Never invent figures — if the
tools can't answer something, say so and suggest what data would be needed. Resolve relative dates
("last month", "this year") against today's date before calling tools.

Reply in {language}. Be brief: lead with the answer, then at most a few supporting numbers. Use a small
markdown table only when comparing several items. Round money to whole euros unless cents matter."""


@router.post("/chat")
def chat(body: ChatRequest, user_id: str = Depends(get_current_user)):
    check_business_access(user_id, body.business_id)
    if body.messages[-1].role != "user":
        raise HTTPException(400, "The last message must be from the user")
    ai.consume_quota(body.business_id, "chat")
    business = supabase.table("businesses").select("name").eq("id", body.business_id).single().execute().data

    try:
        runner = ai.client().beta.messages.tool_runner(
            **ai.request_options(),
            max_tokens=16000,
            output_config={"effort": "medium"},
            system=CHAT_SYSTEM.format(business=business["name"], today=date.today().isoformat(),
                                      language="Greek" if body.language == "el" else "English"),
            tools=_build_tools(body.business_id),
            messages=[m.model_dump() for m in body.messages],
        )
        final = None
        for message in runner:
            final = message
    except anthropic.APIError as e:
        ai.raise_for_api_error(e)

    if final is None or final.stop_reason == "refusal":
        raise HTTPException(422, "The assistant couldn't answer that")
    return {"reply": ai.text_of(final)}


# ── Re-engagement message drafts ──────────────────────────────────────────────

class DraftRequest(BaseModel):
    business_id: str
    customer_name: str = Field(min_length=1, max_length=200)
    language: Literal["el", "en"] = "el"
    channel: Literal["email", "sms"] = "email"
    offer: Optional[str] = Field(default=None, max_length=300)


@router.post("/draft-message")
def draft_message(body: DraftRequest, user_id: str = Depends(get_current_user)):
    check_business_access(user_id, body.business_id)
    business = supabase.table("businesses").select("name").eq("id", body.business_id).single().execute().data

    since = datetime.now(timezone.utc).date() - timedelta(days=365)
    lines = [l for l in _sales_lines(body.business_id, since, datetime.now(timezone.utc).date())
             if l["customer"] == body.customer_name]
    if not lines:
        raise HTTPException(404, "No sales to this customer in the last year")
    top: dict[str, int] = defaultdict(int)
    for l in lines:
        top[(l.get("products") or {}).get("name") or "?"] += l["quantity"]
    facts = {
        "orders_last_year": len({l["order_id"] for l in lines}),
        "last_order_date": max(l["day"] for l in lines),
        "products_they_buy": [k for k, _ in sorted(top.items(), key=lambda kv: -kv[1])[:5]],
    }

    ai.consume_quota(body.business_id, "draft_message")
    length = "under 300 characters, no subject line" if body.channel == "sms" else \
        "a subject line, then 80–140 words"
    prompt = f"""Write a short, warm message from the business "{business['name']}" to its customer "{body.customer_name}",
who used to order regularly but hasn't recently. Purpose: check in and make it easy to reorder.

Facts (use only these, don't invent others): {json.dumps(facts, ensure_ascii=False)}
Offer to mention: {body.offer or "none — do not invent discounts or promotions"}

Format: {body.channel}, {length}. Language: {"Greek" if body.language == "el" else "English"}.
Sound like a person who knows the customer, not a marketing campaign. No placeholders like [Name] —
sign off with the business name. Return only the message."""
    try:
        response = ai.client().beta.messages.create(
            **ai.request_options(),
            max_tokens=2000,
            output_config={"effort": "low"},
            messages=[{"role": "user", "content": prompt}],
        )
    except anthropic.APIError as e:
        ai.raise_for_api_error(e)
    if response.stop_reason == "refusal":
        raise HTTPException(422, "Couldn't draft a message")
    return {"message": ai.text_of(response), "facts": facts}
