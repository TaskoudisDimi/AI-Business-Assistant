from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from db.supabase_client import supabase  

class RefreshSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)

        access_token = request.cookies.get("access_token")
        refresh_token = request.cookies.get("refresh_token")

        if not access_token and not refresh_token:
            return response

        try:
            supabase.auth.get_user(access_token)
            return response
        except Exception as e:
            if refresh_token:
                try:
                    refreshed = supabase.auth.refresh_session(refresh_token=refresh_token)
                    if refreshed.session:
                        response.set_cookie(
                            key="access_token",
                            value=refreshed.session.access_token,
                            httponly=True,
                            secure=False, 
                            samesite="lax",
                            max_age=3600 * 24 * 7, 
                        )
                        response.set_cookie(
                            key="refresh_token",
                            value=refreshed.session.refresh_token,
                            httponly=True,
                            secure=False,
                            samesite="lax",
                            max_age=3600 * 24 * 30,  
                        )
                    else:
                        response.delete_cookie("access_token")
                        response.delete_cookie("refresh_token")
                except Exception as refresh_err:
                    response.delete_cookie("access_token")
                    response.delete_cookie("refresh_token")

        return response