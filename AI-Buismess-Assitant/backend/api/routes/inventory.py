from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta, timezone
from core.security import get_current_user
from db.supabase_client import supabase

router = APIRouter(prefix="/api/inventory", tags=["Inventory"])


def _check_biz(business_id: str, user_id: str):
    m = supabase.table("business_members") \
        .select("role").eq("user_id", user_id).eq("business_id", business_id) \
        .maybe_single().execute()
    if not m.data:
        raise HTTPException(403, "Access denied")


@router.get("")
async def list_inventory(business_id: str, user_id: str = Depends(get_current_user)):
    _check_biz(business_id, user_id)
    res = supabase.table("inventory_items") \
        .select("*, products(id, sku, name, category, unit, reorder_point, cost_price, sell_price)") \
        .eq("business_id", business_id).execute()
    return res.data or []


class MovementCreate(BaseModel):
    business_id: str
    product_id: str
    type: str
    quantity: int
    reason: Optional[str] = None
    order_id: Optional[str] = None


@router.post("/movement")
async def record_movement(body: MovementCreate, user_id: str = Depends(get_current_user)):
    _check_biz(body.business_id, user_id)

    if body.type not in ("inbound", "outbound", "adjustment"):
        raise HTTPException(400, "Invalid movement type")

    inv = supabase.table("inventory_items") \
        .select("id, quantity") \
        .eq("product_id", body.product_id) \
        .eq("business_id", body.business_id) \
        .maybe_single().execute()

    if not inv.data:
        raise HTTPException(404, "Inventory item not found")

    current_qty = inv.data["quantity"]
    if body.type == "inbound":
        new_qty = current_qty + body.quantity
    elif body.type == "outbound":
        new_qty = max(0, current_qty - body.quantity)
    else:
        new_qty = body.quantity

    movement = supabase.table("inventory_movements").insert({
        "product_id": body.product_id,
        "business_id": body.business_id,
        "type": body.type,
        "quantity": body.quantity,
        "reason": body.reason,
        "order_id": body.order_id,
        "created_by": user_id,
    }).execute()

    supabase.table("inventory_items") \
        .update({"quantity": new_qty, "last_updated": datetime.now(timezone.utc).isoformat()}) \
        .eq("id", inv.data["id"]).execute()

    return {"movement": movement.data[0] if movement.data else {}, "new_quantity": new_qty}


@router.get("/movements")
async def list_movements(
    business_id: str,
    product_id: Optional[str] = None,
    user_id: str = Depends(get_current_user),
):
    _check_biz(business_id, user_id)
    query = supabase.table("inventory_movements") \
        .select("*, products(sku, name)") \
        .eq("business_id", business_id) \
        .order("created_at", desc=True) \
        .limit(200)
    if product_id:
        query = query.eq("product_id", product_id)
    return query.execute().data or []


@router.get("/reorder-suggestions")
async def reorder_suggestions(business_id: str, user_id: str = Depends(get_current_user)):
    _check_biz(business_id, user_id)

    inv_res = supabase.table("inventory_items") \
        .select("quantity, products(id, sku, name, category, unit, reorder_point)") \
        .eq("business_id", business_id).execute()

    if not inv_res.data:
        return []

    since = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    movements_res = supabase.table("inventory_movements") \
        .select("product_id, quantity") \
        .eq("business_id", business_id) \
        .eq("type", "outbound") \
        .gte("created_at", since).execute()

    outbound_by_product: dict = {}
    for m in (movements_res.data or []):
        pid = m["product_id"]
        outbound_by_product[pid] = outbound_by_product.get(pid, 0) + m["quantity"]

    suggestions = []
    for item in inv_res.data:
        product = item.get("products")
        if not product:
            continue

        current_stock = item["quantity"]
        reorder_point = product.get("reorder_point", 0)
        total_out_30d = outbound_by_product.get(product["id"], 0)
        avg_daily = total_out_30d / 30

        days_until_stockout = round(current_stock / avg_daily, 1) if avg_daily > 0 else None

        if current_stock <= reorder_point or (days_until_stockout is not None and days_until_stockout < 7):
            urgency = "critical"
        elif days_until_stockout is not None and days_until_stockout < 14:
            urgency = "warning"
        else:
            urgency = "ok"

        if urgency != "ok":
            suggestions.append({
                "product_id": product["id"],
                "sku": product["sku"],
                "name": product["name"],
                "category": product.get("category"),
                "unit": product.get("unit"),
                "current_stock": current_stock,
                "reorder_point": reorder_point,
                "avg_daily_outbound": round(avg_daily, 2),
                "days_until_stockout": days_until_stockout,
                "urgency": urgency,
            })

    suggestions.sort(key=lambda x: (0 if x["urgency"] == "critical" else 1, x.get("days_until_stockout") or 999))
    return suggestions
