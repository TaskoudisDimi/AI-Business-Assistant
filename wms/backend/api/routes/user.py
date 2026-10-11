from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from db.supabase_client import supabase, new_auth_client
from core.security import get_current_user

router = APIRouter(prefix="/api/user", tags=["User"])


class UpdateUserSchema(BaseModel):
    full_name: str | None = None
    username: str | None = None
    language: str | None = None


@router.patch("")
def update_user(data: UpdateUserSchema,
                user_id: str = Depends(get_current_user)):

    update_data = data.dict(exclude_none=True)
    if not update_data:
        raise HTTPException(400, "No fields to update")

    supabase.table("users") \
        .update(update_data) \
        .eq("id", user_id) \
        .execute()

    user = supabase.table("users") \
        .select("*") \
        .eq("id", user_id) \
        .single() \
        .execute()

    return user.data


class ChangeEmailSchema(BaseModel):
    email: EmailStr


@router.patch("/email")
def change_email(data: ChangeEmailSchema,
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
    current_password: str = Field(min_length=1)
    password: str = Field(min_length=8)


@router.patch("/password")
def change_password(data: ChangePasswordSchema,
                    user_id: str = Depends(get_current_user)):

    # Re-check the current password so a hijacked session can't lock the owner out
    try:
        email = supabase.auth.admin.get_user_by_id(user_id).user.email
        new_auth_client().auth.sign_in_with_password({"email": email, "password": data.current_password})
    except Exception:
        raise HTTPException(400, "Current password is incorrect")

    try:
        supabase.auth.admin.update_user_by_id(
            user_id,
            {"password": data.password}
        )
        return {"message": "Password updated"}
    except Exception as e:
        raise HTTPException(400, str(e))
    
@router.delete("")
def delete_account(user_id: str = Depends(get_current_user)):

    supabase.auth.admin.delete_user(user_id)

    return {"message": "Account deleted"}