import logging
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field

from core.config import FRONTEND_URL
from core.security import get_current_user
from db.supabase_client import supabase
from services import mailer
from services.permissions import check_business_access

router = APIRouter(prefix="/api/businesses", tags=["Businesses"])
log = logging.getLogger(__name__)


class CreateBusinessSchema(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    industry: str | None = None


class UpdateBusinessSchema(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    industry: str | None = None
    alert_email_enabled: bool | None = None


class InviteSchema(BaseModel):
    email: EmailStr
    role: Literal["member", "admin"] = "member"


class RoleSchema(BaseModel):
    role: Literal["member", "admin"]


@router.get("")
def get_my_businesses(user_id: str = Depends(get_current_user)):
    memberships = supabase.table("business_members") \
        .select("business_id") \
        .eq("user_id", user_id) \
        .execute()
    business_ids = [m["business_id"] for m in memberships.data]
    if not business_ids:
        return []
    return supabase.table("businesses").select("*").in_("id", business_ids).execute().data


@router.post("")
def create_business(data: CreateBusinessSchema, user_id: str = Depends(get_current_user)):
    business = supabase.table("businesses").insert({
        "owner_id": user_id,
        "name": data.name,
        "industry": data.industry,
    }).execute().data[0]
    supabase.table("business_members").insert({
        "business_id": business["id"],
        "user_id": user_id,
        "role": "owner",
    }).execute()
    return business


@router.patch("/{business_id}")
def update_business(business_id: str, data: UpdateBusinessSchema, user_id: str = Depends(get_current_user)):
    check_business_access(user_id, business_id, min_role="admin")
    fields = data.model_dump(exclude_none=True)
    if not fields:
        raise HTTPException(400, "No fields to update")
    supabase.table("businesses").update(fields).eq("id", business_id).execute()
    return supabase.table("businesses").select("*").eq("id", business_id).single().execute().data


@router.delete("/{business_id}")
def delete_business(business_id: str, user_id: str = Depends(get_current_user)):
    check_business_access(user_id, business_id, min_role="owner")
    supabase.table("businesses").delete().eq("id", business_id).execute()
    return {"message": "Deleted"}


# ── Team ──────────────────────────────────────────────────────────────────────

def _find_user_by_email(email: str):
    """GoTrue has no lookup-by-email endpoint, so page through users.
    Fine for small user bases; switch to an RPC on auth.users if this grows."""
    page = 1
    while True:
        users = supabase.auth.admin.list_users(page=page, per_page=1000)
        for u in users:
            if (u.email or "").lower() == email.lower():
                return u
        if len(users) < 1000:
            return None
        page += 1


@router.get("/{business_id}/members")
def list_members(business_id: str, user_id: str = Depends(get_current_user)):
    check_business_access(user_id, business_id)
    rows = supabase.table("business_members").select("user_id, role, created_at") \
        .eq("business_id", business_id).order("created_at").execute().data or []
    profiles = {p["id"]: p for p in (supabase.table("users").select("id, full_name")
                .in_("id", [r["user_id"] for r in rows]).execute().data or [])} if rows else {}
    members = []
    for r in rows:
        try:
            auth_user = supabase.auth.admin.get_user_by_id(r["user_id"]).user
            email = auth_user.email
            pending = auth_user.last_sign_in_at is None
        except Exception:
            email, pending = None, False
        members.append({
            "user_id": r["user_id"], "role": r["role"], "joined_at": r["created_at"],
            "email": email, "full_name": (profiles.get(r["user_id"]) or {}).get("full_name"),
            "pending": pending, "is_you": r["user_id"] == user_id,
        })
    return members


@router.post("/{business_id}/members")
def invite_member(business_id: str, data: InviteSchema, user_id: str = Depends(get_current_user)):
    check_business_access(user_id, business_id, min_role="admin")
    business = supabase.table("businesses").select("name").eq("id", business_id).single().execute().data

    existing = _find_user_by_email(data.email)
    if existing:
        already = supabase.table("business_members").select("id") \
            .eq("business_id", business_id).eq("user_id", existing.id).maybe_single().execute()
        if already and already.data:
            raise HTTPException(409, "Already a member")
        target_id, invited = existing.id, False
    else:
        try:
            # Supabase emails an invite link; it lands on /reset-password (#type=invite)
            # where the new member picks a password.
            res = supabase.auth.admin.invite_user_by_email(data.email, {
                "redirect_to": f"{FRONTEND_URL}/reset-password",
                "data": {"invited_to": business["name"]},
            })
        except Exception as e:
            log.exception("invite_user_by_email failed")
            raise HTTPException(400, f"Could not send invite: {e}")
        target_id, invited = res.user.id, True

    supabase.table("business_members").insert({
        "business_id": business_id, "user_id": target_id, "role": data.role,
    }).execute()

    if not invited and mailer.is_configured():
        mailer.send_template(data.email, "added_to_team", lang="el",
                             business=business["name"], url=f"{FRONTEND_URL}/login")
    return {"user_id": target_id, "invited": invited}


@router.patch("/{business_id}/members/{member_id}")
def change_role(business_id: str, member_id: str, data: RoleSchema, user_id: str = Depends(get_current_user)):
    check_business_access(user_id, business_id, min_role="admin")
    target = supabase.table("business_members").select("role") \
        .eq("business_id", business_id).eq("user_id", member_id).maybe_single().execute()
    if not target or not target.data:
        raise HTTPException(404, "Member not found")
    if target.data["role"] == "owner":
        raise HTTPException(400, "The owner's role can't be changed")
    supabase.table("business_members").update({"role": data.role}) \
        .eq("business_id", business_id).eq("user_id", member_id).execute()
    return {"ok": True}


@router.delete("/{business_id}/members/{member_id}")
def remove_member(business_id: str, member_id: str, user_id: str = Depends(get_current_user)):
    # Anyone can leave; removing someone else needs admin
    check_business_access(user_id, business_id, min_role="member" if member_id == user_id else "admin")
    target = supabase.table("business_members").select("role") \
        .eq("business_id", business_id).eq("user_id", member_id).maybe_single().execute()
    if not target or not target.data:
        raise HTTPException(404, "Member not found")
    if target.data["role"] == "owner":
        raise HTTPException(400, "The owner can't be removed")
    supabase.table("business_members").delete() \
        .eq("business_id", business_id).eq("user_id", member_id).execute()
    return {"ok": True}
