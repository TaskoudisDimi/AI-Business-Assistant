import base64
import json

from fastapi import Request, Response, HTTPException
from db.supabase_client import supabase
from core.config import COOKIE_SECURE

ACCESS_MAX_AGE = 3600 * 24 * 7
REFRESH_MAX_AGE = 3600 * 24 * 30


def jwt_claims(token: str) -> dict:
    """Decode a JWT payload WITHOUT verifying the signature. Only use it on tokens
    that are also verified (get_user) or where a forged token can do no harm."""
    payload = token.split(".")[1]
    payload += "=" * (-len(payload) % 4)
    return json.loads(base64.urlsafe_b64decode(payload))


def set_auth_cookies(response: Response, session) -> None:
    response.set_cookie(
        key="access_token",
        value=session.access_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        max_age=ACCESS_MAX_AGE,
    )
    response.set_cookie(
        key="refresh_token",
        value=session.refresh_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        max_age=REFRESH_MAX_AGE,
    )


def clear_auth_cookies(response: Response) -> None:
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")


def get_current_user(request: Request):

    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        user_res = supabase.auth.get_user(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Authentication failed")

    if not user_res or not user_res.user:
        raise HTTPException(status_code=401, detail="Invalid session")

    return user_res.user.id
