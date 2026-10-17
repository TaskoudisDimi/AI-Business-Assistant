from datetime import datetime, timedelta, timezone

from core.config import FRONTEND_URL
from db.supabase_client import supabase
from services import mailer
from services.forecasting import detect_anomalies, plan_reorders, plan_to_dict

EXPIRY_WARNING_DAYS = 14


def build_digest(business_id: str) -> dict:
    reorder = [plan_to_dict(p) for p in plan_reorders(business_id) if p.urgency != "ok"]
    until = (datetime.now(timezone.utc).date() + timedelta(days=EXPIRY_WARNING_DAYS)).isoformat()
    expiring = supabase.table("inventory_lots").select("lot_code, expiry_date, quantity, products(sku, name)") \
        .eq("business_id", business_id).gt("quantity", 0).lte("expiry_date", until) \
        .order("expiry_date").execute().data or []
    anomalies = [a for a in detect_anomalies(business_id) if a["severity"] != "info"]
    return {"reorder": reorder, "expiring": expiring, "anomalies": anomalies,
            "count": len(reorder) + len(expiring) + len(anomalies)}


def recipients(business_id: str) -> list[tuple[str, str]]:
    """(email, language) for owners and admins."""
    rows = supabase.table("business_members").select("user_id") \
        .eq("business_id", business_id).in_("role", ["owner", "admin"]).execute().data or []
    langs = {u["id"]: u.get("language") or "el" for u in (supabase.table("users").select("id, language")
             .in_("id", [r["user_id"] for r in rows]).execute().data or [])} if rows else {}
    out = []
    for r in rows:
        try:
            email = supabase.auth.admin.get_user_by_id(r["user_id"]).user.email
        except Exception:
            continue
        if email:
            out.append((email, langs.get(r["user_id"], "el")))
    return out


def send_digest(business_id: str, business_name: str, to: list[tuple[str, str]], digest: dict | None = None) -> int:
    digest = digest or build_digest(business_id)
    for email, lang in to:
        subject, text, html_body = mailer.render_alert_digest(
            lang, business_name, digest["reorder"], digest["expiring"], digest["anomalies"], f"{FRONTEND_URL}/inventory")
        mailer.send(email, subject, text, html_body)
    return len(to)
