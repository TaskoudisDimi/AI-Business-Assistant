from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from core.security import get_current_user
from db.supabase_client import supabase

router = APIRouter(prefix="/businesses", tags=["Businesses"])


# =========================
# Schemas
# =========================

class CreateBusinessSchema(BaseModel):
    name: str
    industry: str | None = None


class UpdateBusinessSchema(BaseModel):
    name: str | None = None
    industry: str | None = None


class InviteMemberSchema(BaseModel):
    user_id: str
    role: str = "member"


# =========================
# Get All My Businesses
# =========================

@router.get("")
async def get_my_businesses(user_id: str = Depends(get_current_user)):

    memberships = supabase.table("business_members") \
        .select("business_id") \
        .eq("user_id", user_id) \
        .execute()

    business_ids = [m["business_id"] for m in memberships.data]

    if not business_ids:
        return []

    businesses = supabase.table("businesses") \
        .select("*") \
        .in_("id", business_ids) \
        .execute()

    return businesses.data


# =========================
# Create Business
# =========================

@router.post("")
async def create_business(data: CreateBusinessSchema,
                          user_id: str = Depends(get_current_user)):

    business = supabase.table("businesses").insert({
        "owner_id": user_id,
        "name": data.name,
        "industry": data.industry
    }).execute()

    created_business = business.data[0]

    # Add creator as owner in members
    supabase.table("business_members").insert({
        "business_id": created_business["id"],
        "user_id": user_id,
        "role": "owner"
    }).execute()

    return created_business


# =========================
# Update Business
# =========================

@router.patch("/{business_id}")
async def update_business(business_id: str,
                          data: UpdateBusinessSchema,
                          user_id: str = Depends(get_current_user)):

    membership = supabase.table("business_members") \
        .select("*") \
        .eq("business_id", business_id) \
        .eq("user_id", user_id) \
        .maybe_single() \
        .execute()

    if not membership.data:
        raise HTTPException(403, "Not allowed")

    updated = supabase.table("businesses") \
        .update(data.dict(exclude_none=True)) \
        .eq("id", business_id) \
        .execute()

    return updated.data[0]


# =========================
# Delete Business
# =========================

@router.delete("/{business_id}")
async def delete_business(business_id: str,
                          user_id: str = Depends(get_current_user)):

    business = supabase.table("businesses") \
        .select("*") \
        .eq("id", business_id) \
        .eq("owner_id", user_id) \
        .maybe_single() \
        .execute()

    if not business.data:
        raise HTTPException(403, "Only owner can delete")

    supabase.table("businesses") \
        .delete() \
        .eq("id", business_id) \
        .execute()

    return {"message": "Deleted"}


# =========================
# Invite Member
# =========================

@router.post("/{business_id}/invite")
async def invite_member(business_id: str,
                        data: InviteMemberSchema,
                        user_id: str = Depends(get_current_user)):

    # only owner
    business = supabase.table("businesses") \
        .select("*") \
        .eq("id", business_id) \
        .eq("owner_id", user_id) \
        .maybe_single() \
        .execute()

    if not business.data:
        raise HTTPException(403, "Only owner can invite")

    supabase.table("business_members").insert({
        "business_id": business_id,
        "user_id": data.user_id,
        "role": data.role
    }).execute()

    return {"message": "Invited"}