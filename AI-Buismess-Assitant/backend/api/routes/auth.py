from fastapi import APIRouter, HTTPException, Response, Depends
from db.supabase_client import supabase
from core.security import get_current_user
from pydantic import BaseModel, EmailStr, Field

router = APIRouter()

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    full_name: str = Field(min_length=6)
    
@router.post("/register")
def register(data: RegisterRequest):

    res = supabase.auth.sign_up({
        "email": data.email,
        "password": data.password,
        "options": {
            "data": {
                "full_name": data.full_name
            },
            "email_redirect_to": "http://localhost:5173/confirm"
        }
    })

    if res.error:
        if "already registered" in res.error.message.lower():
            raise HTTPException(status_code=400, detail="Email already registered")
        raise HTTPException(status_code=400, detail=res.error.message)

    if not res.user:
        raise HTTPException(status_code=400, detail="Registration failed")

    supabase.table("users").insert({
        "id": res.user.id,
        "full_name": data.full_name
    }).execute()

    return {"message": "Registered successfully"}

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out"}

@router.get("/dashboard")
def dashboard(user_id: str = Depends(get_current_user)):
    return {"message": "Protected data"}

@router.post("/login")
def login(data: LoginRequest, response: Response):

    res = supabase.auth.sign_in_with_password({
        "email": data.email,
        "password": data.password
    })

    if not res.session:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = res.session.access_token

 
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  
        samesite="lax"
    )

    return {"message": "Logged in successfully"}