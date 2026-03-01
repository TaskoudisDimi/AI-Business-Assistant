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