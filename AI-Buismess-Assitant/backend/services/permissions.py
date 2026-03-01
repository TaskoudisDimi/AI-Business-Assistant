from fastapi import HTTPException
from db.supabase_client import supabase


def check_business_access(user_id: str, business_id: str):

    membership = supabase.table("business_members") \
        .select("id") \
        .eq("business_id", business_id) \
        .eq("user_id", user_id) \
        .maybe_single() \
        .execute()

    if not membership.data:
        raise HTTPException(status_code=403, detail="No access to this business")