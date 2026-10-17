from fastapi import APIRouter, Depends, HTTPException

from core.security import get_current_user
from db.supabase_client import supabase
from services import mailer
from services.alerts import build_digest, send_digest
from services.permissions import check_business_access

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])


@router.get("/preview")
def preview(business_id: str, user_id: str = Depends(get_current_user)):
    check_business_access(user_id, business_id)
    return {**build_digest(business_id), "smtp_configured": mailer.is_configured()}


@router.post("/test")
def send_test(business_id: str, user_id: str = Depends(get_current_user)):
    """Send today's digest to the current user only, even if there's nothing to report."""
    check_business_access(user_id, business_id, min_role="admin")
    if not mailer.is_configured():
        raise HTTPException(400, "Email sending is not configured on the server")
    business = supabase.table("businesses").select("name").eq("id", business_id).single().execute().data
    email = supabase.auth.admin.get_user_by_id(user_id).user.email
    profile = supabase.table("users").select("language").eq("id", user_id).maybe_single().execute()
    lang = (profile.data.get("language") if profile and profile.data else None) or "el"
    send_digest(business_id, business["name"], [(email, lang)])
    return {"sent_to": email}
