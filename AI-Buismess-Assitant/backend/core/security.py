from fastapi import Request, HTTPException
from db.supabase_client import supabase


def get_current_user(request: Request):

    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        user_res = supabase.auth.get_user(token)

        if not user_res or not user_res.user:
            raise HTTPException(status_code=401, detail="Invalid session")

        return user_res.user.id

    except Exception:
        raise HTTPException(status_code=401, detail="Authentication failed")