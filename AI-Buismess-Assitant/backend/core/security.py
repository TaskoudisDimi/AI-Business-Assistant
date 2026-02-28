from fastapi import Request, HTTPException, Depends
from db.supabase_client import supabase

def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        user_res = supabase.auth.get_user(token)
        return user_res.user.id
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")