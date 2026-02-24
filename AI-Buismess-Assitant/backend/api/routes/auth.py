from fastapi import APIRouter, HTTPException, Response, Depends
from pydantic import BaseModel
from db.supabase_client import supabase
from core.security import get_current_user

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str

@router.post("/register")
def register(data: RegisterRequest):
    res = supabase.auth.sign_up({
        "email": data.email,
        "password": data.password
    })

    if not res.user:
        raise HTTPException(status_code=400, detail="Registration failed")

    supabase.table("users").insert({
        "id": res.user.id,
        "full_name": data.full_name
    }).execute()

    return {"message": "Registered successfully"}


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
        secure=True,  
        samesite="lax"
    )

    return {"message": "Logged in successfully"}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out"}