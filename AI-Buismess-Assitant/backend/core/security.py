from fastapi import Request, HTTPException
from db.supabase_client import supabase


def get_current_user(request: Request):
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        user_response = supabase.auth.get_user(token)

        if not user_response.user:
            raise HTTPException(status_code=401, detail="Invalid token")

        return user_response.user.id

    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")