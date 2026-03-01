from fastapi import APIRouter, HTTPException, Response, Depends, Request
from pydantic import BaseModel, EmailStr, Field
from db.supabase_client import supabase
from core.security import get_current_user


router = APIRouter(prefix="/api/auth", tags=["Auth"]) 

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    full_name: str = Field(min_length=6)

@router.post("/register")
async def register(data: RegisterRequest, response: Response):
    try:
        sign_up_res = supabase.auth.sign_up({
            "email": data.email,
            "password": data.password,
            "options": {
                "data": {"full_name": data.full_name},
                "email_redirect_to": "http://localhost:5173/login" 
            }
        })

        if sign_up_res.user:
            if sign_up_res.user.confirmed_at:
                return {"message": "Registration successful - you can login now"}
            else:
                return {"message": "Confirmation email sent - check your inbox/spam"}
        else:
            raise HTTPException(400, "Signup failed")
    except Exception as e:
        raise HTTPException(400, detail=str(e))
    

@router.post("/login")
async def login(data: LoginRequest, response: Response):
    try:
        res = supabase.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password
        })

        if not res.session:
            raise HTTPException(401, "Invalid credentials")

        response.set_cookie(
            key="access_token",
            value=res.session.access_token,
            httponly=True,
            secure=False,         
            samesite="lax",
            max_age=3600 * 24 * 7 
        )
        response.set_cookie(
            key="refresh_token",
            value=res.session.refresh_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=3600 * 24 * 30 
        )

        return {"message": "Logged in"}
    except Exception:
        raise HTTPException(401, "Invalid credentials")


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    supabase.auth.sign_out()  
    return {"message": "Logged out"}


@router.get("/me")
async def get_me(user_id: str = Depends(get_current_user)):

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

    businesses = supabase.table("businesses") \
        .select("*") \
        .in_("id", business_ids) \
        .execute()

    return {
        "user": user.data,
        "businesses": businesses.data,
        "memberships": memberships.data
    }