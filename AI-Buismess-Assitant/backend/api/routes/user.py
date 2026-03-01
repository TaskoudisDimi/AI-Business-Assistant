from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from db.supabase_client import supabase
from core.security import get_current_user

router = APIRouter(prefix="/api/user", tags=["User"])


class UpdateUserSchema(BaseModel):
    full_name: str | None = None
    username: str | None = None
    language: str | None = None


@router.patch("")
async def update_user(data: UpdateUserSchema,
                      user_id: str = Depends(get_current_user)):

    updated = supabase.table("users") \
        .update(data.dict(exclude_none=True)) \
        .eq("id", user_id) \
        .execute()

    return updated.data[0]


class ChangeEmailSchema(BaseModel):
    email: EmailStr


@router.patch("/email")
async def change_email(data: ChangeEmailSchema,
                       user_id: str = Depends(get_current_user)):

    try:
        supabase.auth.admin.update_user_by_id(
            user_id,
            {"email": data.email}
        )
        return {"message": "Email update requested"}
    except Exception as e:
        raise HTTPException(400, str(e))
    
class ChangePasswordSchema(BaseModel):
    password: str


@router.patch("/password")
async def change_password(data: ChangePasswordSchema,
                          user_id: str = Depends(get_current_user)):

    try:
        supabase.auth.admin.update_user_by_id(
            user_id,
            {"password": data.password}
        )
        return {"message": "Password updated"}
    except Exception as e:
        raise HTTPException(400, str(e))
    
@router.delete("")
async def delete_account(user_id: str = Depends(get_current_user)):

    supabase.auth.admin.delete_user(user_id)

    return {"message": "Account deleted"}