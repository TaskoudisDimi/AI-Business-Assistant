from fastapi import Request, HTTPException
from jose import jwt, JWTError
from core.config import SUPABASE_JWT_SECRET

def get_current_user(request: Request):
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated"
        )
        return payload.get("sub")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")