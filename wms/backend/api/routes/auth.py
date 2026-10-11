import logging
from fastapi import APIRouter, HTTPException, Request, Response, Depends
from pydantic import BaseModel, EmailStr, Field
from db.supabase_client import supabase, new_auth_client
from core.config import FRONTEND_URL
from core.security import get_current_user, jwt_claims, set_auth_cookies, clear_auth_cookies


router = APIRouter(prefix="/api/auth", tags=["Auth"])
log = logging.getLogger(__name__)

MIN_PASSWORD_LENGTH = 8


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=MIN_PASSWORD_LENGTH)
    full_name: str = Field(min_length=2, max_length=120)

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    password: str = Field(min_length=MIN_PASSWORD_LENGTH)
    # One of the two, depending on how the Supabase email template builds the link:
    # - default template → implicit flow → access_token in the URL fragment
    # - custom template with {{ .TokenHash }} → token_hash in the query string
    access_token: str | None = None
    token_hash: str | None = None


@router.post("/register")
def register(data: RegisterRequest):
    try:
        sign_up_res = new_auth_client().auth.sign_up({
            "email": data.email,
            "password": data.password,
            "options": {
                "data": {"full_name": data.full_name.strip()},
                "email_redirect_to": f"{FRONTEND_URL}/login",
            }
        })
    except Exception as e:
        raise HTTPException(400, detail=str(e))

    if not sign_up_res.user:
        raise HTTPException(400, "Signup failed")
    if sign_up_res.user.confirmed_at:
        return {"message": "Registration successful - you can login now", "confirmed": True}
    return {"message": "Confirmation email sent - check your inbox/spam", "confirmed": False}


@router.post("/login")
def login(data: LoginRequest, response: Response):
    try:
        res = new_auth_client().auth.sign_in_with_password({
            "email": data.email,
            "password": data.password
        })
    except Exception:
        raise HTTPException(401, "Invalid credentials")

    if not res.session:
        raise HTTPException(401, "Invalid credentials")

    set_auth_cookies(response, res.session)
    return {"message": "Logged in"}


@router.post("/logout")
def logout(request: Request, response: Response):
    token = request.cookies.get("access_token")
    if token:
        try:
            # Revokes the refresh token server-side, so a stolen cookie stops working too
            supabase.auth.admin.sign_out(token)
        except Exception:
            pass
    clear_auth_cookies(response)
    return {"message": "Logged out"}


@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest):
    try:
        new_auth_client().auth.reset_password_for_email(
            data.email,
            {"redirect_to": f"{FRONTEND_URL}/reset-password"},
        )
    except Exception:
        # Don't reveal whether the address exists; log for debugging (rate limits, SMTP errors)
        log.exception("reset_password_for_email failed")
    return {"message": "If an account exists for this email, a reset link has been sent"}


@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, response: Response):
    client = new_auth_client()
    session = None
    try:
        if data.token_hash:
            session = client.auth.verify_otp({"token_hash": data.token_hash, "type": "recovery"}).session
            user_id = session.user.id if session else None
        elif data.access_token:
            user_res = supabase.auth.get_user(data.access_token)  # verifies the token
            # Only accept sessions created by a recovery link, not a normal login
            # session (that would let a stolen cookie change the password)
            methods = {a.get("method") for a in jwt_claims(data.access_token).get("amr", [])}
            if user_res and user_res.user and "recovery" in methods:
                user_id = user_res.user.id
            else:
                user_id = None
        else:
            user_id = None
    except Exception:
        user_id = None

    if not user_id:
        raise HTTPException(400, "Reset link is invalid or has expired")

    try:
        supabase.auth.admin.update_user_by_id(user_id, {"password": data.password})
    except Exception as e:
        raise HTTPException(400, detail=str(e))

    # Recovery link proves ownership of the email — sign the user in right away
    if session:
        set_auth_cookies(response, session)
    return {"message": "Password updated"}


@router.get("/me")
def get_me(user_id: str = Depends(get_current_user)):
    user = supabase.table("users") \
        .select("*") \
        .eq("id", user_id) \
        .single() \
        .execute()

    memberships = supabase.table("business_members") \
        .select("business_id, role") \
        .eq("user_id", user_id) \
        .execute()

    business_ids = [m["business_id"] for m in memberships.data]

    # Auto-create a default business if the user has none
    if not business_ids:
        full_name = (user.data or {}).get("full_name") or "My Business"
        biz = supabase.table("businesses").insert({
            "owner_id": user_id,
            "name": full_name,
            "industry": None,
        }).execute()
        created_id = biz.data[0]["id"]
        supabase.table("business_members").insert({
            "business_id": created_id,
            "user_id": user_id,
            "role": "owner",
        }).execute()
        business_ids = [created_id]
        memberships_data = [{"business_id": created_id, "role": "owner"}]
    else:
        memberships_data = memberships.data

    businesses = supabase.table("businesses") \
        .select("*") \
        .in_("id", business_ids) \
        .execute()

    return {
        "user": user.data,
        "businesses": businesses.data,
        "memberships": memberships_data,
    }
