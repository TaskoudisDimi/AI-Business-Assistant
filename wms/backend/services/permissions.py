from fastapi import HTTPException
from db.supabase_client import supabase

# owner > admin > member. Members run the warehouse day to day; admins also manage
# the team and settings; only the owner can delete the business or hand over ownership.
ROLE_RANK = {"member": 1, "admin": 2, "owner": 3}


def get_role(user_id: str, business_id: str) -> str | None:
    membership = supabase.table("business_members") \
        .select("role") \
        .eq("business_id", business_id) \
        .eq("user_id", user_id) \
        .maybe_single() \
        .execute()
    return membership.data["role"] if membership and membership.data else None


def check_business_access(user_id: str, business_id: str, min_role: str = "member") -> str:
    """Raise 403 unless the user belongs to the business with at least `min_role`.
    Returns the user's role."""
    role = get_role(user_id, business_id)
    if not role:
        raise HTTPException(status_code=403, detail="No access to this business")
    if ROLE_RANK.get(role, 0) < ROLE_RANK[min_role]:
        raise HTTPException(status_code=403, detail="Your role can't do this")
    return role
