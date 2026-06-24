from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from core.security import get_current_user
from db.supabase_client import supabase

router = APIRouter(prefix="/api/products", tags=["Products"])


def _check_biz(business_id: str, user_id: str):
    m = supabase.table("business_members") \
        .select("role").eq("user_id", user_id).eq("business_id", business_id) \
        .maybe_single().execute()
    if not m.data:
        raise HTTPException(403, "Access denied")


class ProductCreate(BaseModel):
    business_id: str
    sku: str
    name: str
    category: Optional[str] = None
    unit: str = "τεμ"
    reorder_point: int = 0
    cost_price: Optional[float] = None
    sell_price: Optional[float] = None


class ProductUpdate(BaseModel):
    sku: Optional[str] = None
    name: Optional[str] = None
    category: Optional[str] = None
    unit: Optional[str] = None
    reorder_point: Optional[int] = None
    cost_price: Optional[float] = None
    sell_price: Optional[float] = None


@router.get("")
async def list_products(business_id: str, user_id: str = Depends(get_current_user)):
    _check_biz(business_id, user_id)
    res = supabase.table("products").select("*") \
        .eq("business_id", business_id).order("created_at").execute()
    return res.data or []


@router.post("")
async def create_product(body: ProductCreate, user_id: str = Depends(get_current_user)):
    _check_biz(body.business_id, user_id)
    res = supabase.table("products").insert({
        "business_id": body.business_id,
        "sku": body.sku,
        "name": body.name,
        "category": body.category,
        "unit": body.unit,
        "reorder_point": body.reorder_point,
        "cost_price": body.cost_price,
        "sell_price": body.sell_price,
    }).execute()
    if not res.data:
        raise HTTPException(500, "Failed to create product")
    product = res.data[0]
    supabase.table("inventory_items").insert({
        "product_id": product["id"],
        "business_id": body.business_id,
        "quantity": 0,
    }).execute()
    return product


@router.patch("/{product_id}")
async def update_product(
    product_id: str,
    body: ProductUpdate,
    user_id: str = Depends(get_current_user),
):
    p = supabase.table("products").select("business_id") \
        .eq("id", product_id).maybe_single().execute()
    if not p.data:
        raise HTTPException(404, "Not found")
    _check_biz(p.data["business_id"], user_id)
    fields = {k: v for k, v in {
        "sku": body.sku, "name": body.name, "category": body.category,
        "unit": body.unit, "reorder_point": body.reorder_point,
        "cost_price": body.cost_price, "sell_price": body.sell_price,
    }.items() if v is not None}
    if not fields:
        raise HTTPException(400, "No fields to update")
    res = supabase.table("products").update(fields).eq("id", product_id).execute()
    return res.data[0]


@router.delete("/{product_id}")
async def delete_product(product_id: str, user_id: str = Depends(get_current_user)):
    p = supabase.table("products").select("business_id") \
        .eq("id", product_id).maybe_single().execute()
    if not p.data:
        raise HTTPException(404, "Not found")
    _check_biz(p.data["business_id"], user_id)
    supabase.table("products").delete().eq("id", product_id).execute()
    return {"ok": True}
