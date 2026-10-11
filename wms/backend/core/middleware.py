import time

from fastapi import Request
from starlette.concurrency import run_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware

from core.security import jwt_claims, set_auth_cookies, clear_auth_cookies
from db.supabase_client import new_auth_client

# Refresh a little before the access token actually expires
EXPIRY_LEEWAY_SECONDS = 60


def _token_expired(token: str | None) -> bool:
    """Read the `exp` claim without verifying the signature — only used to decide
    whether to refresh. Verification still happens in get_current_user()."""
    if not token:
        return True
    try:
        return jwt_claims(token)["exp"] < time.time() + EXPIRY_LEEWAY_SECONDS
    except Exception:
        return True


def _replace_request_cookies(request: Request, cookies: dict[str, str]) -> None:
    """Rewrite the Cookie header so the route handler sees the refreshed token."""
    merged = {**request.cookies, **cookies}
    cookie_header = "; ".join(f"{k}={v}" for k, v in merged.items()).encode("latin-1")
    headers = [(k, v) for k, v in request.scope["headers"] if k != b"cookie"]
    headers.append((b"cookie", cookie_header))
    request.scope["headers"] = headers


class RefreshSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        access_token = request.cookies.get("access_token")
        refresh_token = request.cookies.get("refresh_token")

        if not refresh_token or not _token_expired(access_token):
            return await call_next(request)

        try:
            session = (await run_in_threadpool(
                new_auth_client().auth.refresh_session, refresh_token
            )).session
        except Exception:
            session = None

        if not session:
            response = await call_next(request)
            clear_auth_cookies(response)
            return response

        _replace_request_cookies(request, {
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
        })
        response = await call_next(request)
        set_auth_cookies(response, session)
        return response
