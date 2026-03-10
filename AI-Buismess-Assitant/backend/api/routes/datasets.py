# @router.get("/datasets/{business_id}")
# async def get_datasets(
#     business_id: str,
#     user_id: str = Depends(get_current_user)
# ):
#     check_business_access(user_id, business_id)

#     datasets = supabase.table("datasets") \
#         .select("*") \
#         .eq("business_id", business_id) \
#         .execute()

#     return datasets.data


from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from core.security import get_current_user
from db.supabase_client import supabase

router = APIRouter(prefix="/datasets", tags=["Datasets"])

class UploadDatasetSchema(BaseModel):
    name: str
    description: str | None = None
    