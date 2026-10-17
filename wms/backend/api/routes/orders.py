from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from core.security import get_current_user
from db.supabase_client import supabase
from services.permissions import check_business_access
from services.stock import apply_movement

router = APIRouter(prefix="/api/orders", tags=["Orders"])


class OrderItemIn(BaseModel):
    product_id: str
    quantity: int = Field(gt=0)
    unit_price: Optional[float] = Field(default=None, ge=0)
    lot_code: Optional[str] = Field(default=None, max_length=80)
    expiry_date: Optional[date] = None


class OrderCreate(BaseModel):
    business_id: str
    type: str
    party_name: Optional[str] = None
    notes: Optional[str] = None
    items: List[OrderItemIn] = []


class StatusUpdate(BaseModel):
    status: str


@router.get("")
def list_orders(
    business_id: str,
    type: Optional[str] = None,
    status: Optional[str] = None,
    user_id: str = Depends(get_current_user),
):
    check_business_access(user_id, business_id)
    query = supabase.table("orders").select("*") \
        .eq("business_id", business_id).order("created_at", desc=True)
    if type:
        query = query.eq("type", type)
    if status:
        query = query.eq("status", status)
    return query.execute().data or []


@router.post("")
def create_order(body: OrderCreate, user_id: str = Depends(get_current_user)):
    check_business_access(user_id, body.business_id)
    if body.type not in ("purchase", "sale"):
        raise HTTPException(400, "Invalid order type")

    product_ids = {item.product_id for item in body.items}
    if product_ids:
        owned = supabase.table("products").select("id") \
            .eq("business_id", body.business_id).in_("id", list(product_ids)).execute()
        if len(owned.data or []) != len(product_ids):
            raise HTTPException(400, "Unknown product in order")

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
                "lot_code": item.lot_code,
                "expiry_date": item.expiry_date.isoformat() if item.expiry_date else None,
            }
            for item in body.items
        ]).execute()

    return order


@router.get("/{order_id}")
def get_order(order_id: str, user_id: str = Depends(get_current_user)):
    order = supabase.table("orders").select("*") \
        .eq("id", order_id).maybe_single().execute()
    if not order or not order.data:
        raise HTTPException(404, "Order not found")
    check_business_access(user_id, order.data["business_id"])
    items = supabase.table("order_items") \
        .select("*, products(sku, name, unit)") \
        .eq("order_id", order_id).execute()
    return {**order.data, "items": items.data or []}


@router.patch("/{order_id}/status")
def update_status(
    order_id: str,
    body: StatusUpdate,
    user_id: str = Depends(get_current_user),
):
    if body.status not in ("draft", "confirmed", "cancelled"):
        raise HTTPException(400, "Invalid status")
    order = supabase.table("orders").select("*") \
        .eq("id", order_id).maybe_single().execute()
    if not order or not order.data:
        raise HTTPException(404, "Order not found")
    check_business_access(user_id, order.data["business_id"])
    if order.data["status"] == "completed":
        raise HTTPException(400, "Completed orders can't change status")
    res = supabase.table("orders").update({"status": body.status}).eq("id", order_id).execute()
    return res.data[0]


@router.post("/{order_id}/complete")
def complete_order(order_id: str, user_id: str = Depends(get_current_user)):
    order = supabase.table("orders").select("*") \
        .eq("id", order_id).maybe_single().execute()
    if not order or not order.data:
        raise HTTPException(404, "Order not found")
    check_business_access(user_id, order.data["business_id"])

    # Claim the order atomically first, so two concurrent requests can't both
    # apply the stock movements
    claimed = supabase.table("orders").update({"status": "completed"}) \
        .eq("id", order_id).in_("status", ["draft", "confirmed"]).execute()
    if not claimed.data:
        raise HTTPException(400, "Order is already completed or cancelled")

    items = supabase.table("order_items").select("product_id, quantity, lot_code, expiry_date") \
        .eq("order_id", order_id).execute()

    movement_type = "inbound" if order.data["type"] == "purchase" else "outbound"
    for item in (items.data or []):
        apply_movement(
            business_id=order.data["business_id"], product_id=item["product_id"], type=movement_type,
            quantity=item["quantity"], user_id=user_id, reason=f"Order #{order_id[:8]}", order_id=order_id,
            lot_code=item.get("lot_code"), expiry_date=item.get("expiry_date"),
        )

    return claimed.data[0]
