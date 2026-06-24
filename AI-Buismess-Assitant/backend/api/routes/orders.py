from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from core.security import get_current_user
from db.supabase_client import supabase

router = APIRouter(prefix="/api/orders", tags=["Orders"])


def _check_biz(business_id: str, user_id: str):
    m = supabase.table("business_members") \
        .select("role").eq("user_id", user_id).eq("business_id", business_id) \
        .maybe_single().execute()
    if not m.data:
        raise HTTPException(403, "Access denied")


class OrderItemIn(BaseModel):
    product_id: str
    quantity: int
    unit_price: Optional[float] = None


class OrderCreate(BaseModel):
    business_id: str
    type: str
    party_name: Optional[str] = None
    notes: Optional[str] = None
    items: List[OrderItemIn] = []


class StatusUpdate(BaseModel):
    status: str


@router.get("")
async def list_orders(
    business_id: str,
    type: Optional[str] = None,
    status: Optional[str] = None,
    user_id: str = Depends(get_current_user),
):
    _check_biz(business_id, user_id)
    query = supabase.table("orders").select("*") \
        .eq("business_id", business_id).order("created_at", desc=True)
    if type:
        query = query.eq("type", type)
    if status:
        query = query.eq("status", status)
    return query.execute().data or []


@router.post("")
async def create_order(body: OrderCreate, user_id: str = Depends(get_current_user)):
    _check_biz(body.business_id, user_id)
    if body.type not in ("purchase", "sale"):
        raise HTTPException(400, "Invalid order type")

    order_res = supabase.table("orders").insert({
        "business_id": body.business_id,
        "type": body.type,
        "status": "draft",
        "party_name": body.party_name,
        "notes": body.notes,
        "created_by": user_id,
    }).execute()

    if not order_res.data:
        raise HTTPException(500, "Failed to create order")

    order = order_res.data[0]

    if body.items:
        supabase.table("order_items").insert([
            {
                "order_id": order["id"],
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
            }
            for item in body.items
        ]).execute()

    return order


@router.get("/{order_id}")
async def get_order(order_id: str, user_id: str = Depends(get_current_user)):
    order = supabase.table("orders").select("*") \
        .eq("id", order_id).maybe_single().execute()
    if not order.data:
        raise HTTPException(404, "Order not found")
    _check_biz(order.data["business_id"], user_id)
    items = supabase.table("order_items") \
        .select("*, products(sku, name, unit)") \
        .eq("order_id", order_id).execute()
    return {**order.data, "items": items.data or []}


@router.patch("/{order_id}/status")
async def update_status(
    order_id: str,
    body: StatusUpdate,
    user_id: str = Depends(get_current_user),
):
    if body.status not in ("draft", "confirmed", "completed", "cancelled"):
        raise HTTPException(400, "Invalid status")
    order = supabase.table("orders").select("*") \
        .eq("id", order_id).maybe_single().execute()
    if not order.data:
        raise HTTPException(404, "Order not found")
    _check_biz(order.data["business_id"], user_id)
    res = supabase.table("orders").update({"status": body.status}).eq("id", order_id).execute()
    return res.data[0]


@router.post("/{order_id}/complete")
async def complete_order(order_id: str, user_id: str = Depends(get_current_user)):
    order = supabase.table("orders").select("*") \
        .eq("id", order_id).maybe_single().execute()
    if not order.data:
        raise HTTPException(404, "Order not found")
    _check_biz(order.data["business_id"], user_id)

    if order.data["status"] == "completed":
        raise HTTPException(400, "Already completed")
    if order.data["status"] == "cancelled":
        raise HTTPException(400, "Cannot complete a cancelled order")

    items = supabase.table("order_items").select("product_id, quantity") \
        .eq("order_id", order_id).execute()

    movement_type = "inbound" if order.data["type"] == "purchase" else "outbound"
    business_id = order.data["business_id"]

    for item in (items.data or []):
        supabase.table("inventory_movements").insert({
            "product_id": item["product_id"],
            "business_id": business_id,
            "type": movement_type,
            "quantity": item["quantity"],
            "reason": f"Order #{order_id[:8]}",
            "order_id": order_id,
            "created_by": user_id,
        }).execute()

        inv = supabase.table("inventory_items") \
            .select("id, quantity") \
            .eq("product_id", item["product_id"]) \
            .eq("business_id", business_id) \
            .maybe_single().execute()

        if inv.data:
            current = inv.data["quantity"]
            new_qty = current + item["quantity"] if movement_type == "inbound" else max(0, current - item["quantity"])
            supabase.table("inventory_items") \
                .update({"quantity": new_qty}).eq("id", inv.data["id"]).execute()

    res = supabase.table("orders").update({"status": "completed"}).eq("id", order_id).execute()
    return res.data[0]
