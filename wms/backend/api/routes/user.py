from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from db.supabase_client import supabase, new_auth_client
from core.security import get_current_user

router = APIRouter(prefix="/api/user", tags=["User"])


class UpdateUserSchema(BaseModel):
    full_name: str | None = None
    username: str | None = None
    language: str | None = None


@router.patch("")
def update_user(data: UpdateUserSchema,
                user_id: str = Depends(get_current_user)):

    update_data = data.dict(exclude_none=True)
    if not update_data:
        raise HTTPException(400, "No fields to update")

    supabase.table("users") \
        .update(update_data) \
        .eq("id", user_id) \
        .execute()

    user = supabase.table("users") \
        .select("*") \
        .eq("id", user_id) \
        .single() \
        .execute()

    return user.data


class ChangeEmailSchema(BaseModel):
    email: EmailStr


@router.patch("/email")
def change_email(data: ChangeEmailSchema,
                 user_id: str = Depends(get_current_user)):

    try:
        supabase.auth.admin.update_user_by_id(
            user_id,
            {"email": data.email}
        )
        return {"message": "Email update requested"}
    except Exception as e:
        raise HTTPException(400, str(e))
    
class ChangePasswordSchema(BaseModel):
    current_password: str = Field(min_length=1)
    password: str = Field(min_length=8)


@router.patch("/password")
def change_password(data: ChangePasswordSchema,
                    user_id: str = Depends(get_current_user)):

    # Re-check the current password so a hijacked session can't lock the owner out
    try:
        email = supabase.auth.admin.get_user_by_id(user_id).user.email
        new_auth_client().auth.sign_in_with_password({"email": email, "password": data.current_password})
    except Exception:
        raise HTTPException(400, "Current password is incorrect")

    try:
        supabase.auth.admin.update_user_by_id(
            user_id,
            {"password": data.password}
        )
        return {"message": "Password updated"}
    except Exception as e:
        raise HTTPException(400, str(e))
    
@router.get("/export")
def export_my_data(user_id: str = Depends(get_current_user)):
    """GDPR data export: profile plus everything in the businesses this user owns."""
    profile = supabase.table("users").select("*").eq("id", user_id).maybe_single().execute()
    auth_user = supabase.auth.admin.get_user_by_id(user_id).user
    owned = supabase.table("businesses").select("*").eq("owner_id", user_id).execute().data or []
    memberships = supabase.table("business_members").select("business_id, role, created_at") \
        .eq("user_id", user_id).execute().data or []

    businesses = []
    for b in owned:
        bid = b["id"]
        orders = supabase.table("orders").select("*, order_items(*)").eq("business_id", bid).execute().data or []
        businesses.append({
            **b,
            "members": supabase.table("business_members").select("user_id, role, created_at").eq("business_id", bid).execute().data,
            "products": supabase.table("products").select("*").eq("business_id", bid).execute().data,
            "inventory": supabase.table("inventory_items").select("*").eq("business_id", bid).execute().data,
            "lots": supabase.table("inventory_lots").select("*").eq("business_id", bid).execute().data,
            "movements": supabase.table("inventory_movements").select("*").eq("business_id", bid).execute().data,
            "orders": orders,
            "datasets": supabase.table("datasets").select("id, name, rows_count, columns, created_at").eq("business_id", bid).execute().data,
            "predictions": supabase.table("predictions").select("*").eq("business_id", bid).execute().data,
        })
    return {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "account": {"id": user_id, "email": auth_user.email, "created_at": str(auth_user.created_at),
                    "profile": profile.data if profile else None},
        "memberships": memberships,
        "owned_businesses": businesses,
    }


@router.delete("")
def delete_account(user_id: str = Depends(get_current_user)):
    """Delete the account and every business it owns (cascades to products, orders,
    stock…), including uploaded dataset files. Memberships in other businesses go too."""
    owned = supabase.table("businesses").select("id").eq("owner_id", user_id).execute().data or []
    for b in owned:
        paths = [d["storage_path"] for d in (supabase.table("datasets").select("storage_path")
                 .eq("business_id", b["id"]).execute().data or []) if d.get("storage_path")]
        if paths:
            try:
                supabase.storage.from_("datasets").remove(paths)
            except Exception:
                pass
        supabase.table("businesses").delete().eq("id", b["id"]).execute()
    supabase.table("business_members").delete().eq("user_id", user_id).execute()
    supabase.auth.admin.delete_user(user_id)
    return {"message": "Account deleted"}
