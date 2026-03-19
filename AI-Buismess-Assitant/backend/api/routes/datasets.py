from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from core.security import get_current_user
from db.supabase_client import supabase
import uuid

router = APIRouter(prefix="/api/datasets", tags=["Datasets"])


@router.get("")
async def get_datasets(user_id: str = Depends(get_current_user)):
    memberships = supabase.table("business_members") \
        .select("business_id") \
        .eq("user_id", user_id) \
        .execute()

    if not memberships.data:
        return []

    business_ids = [m["business_id"] for m in memberships.data]

    datasets_resp = supabase.table("datasets") \
        .select("id, name, created_at, rows_count") \
        .in_("business_id", business_ids) \
        .order("created_at", desc=True) \
        .execute()

    return datasets_resp.data


@router.post("/upload")
async def upload_dataset(
    file: UploadFile = File(...),
    business_id: str = Form(...),           
    user_id: str = Depends(get_current_user)
):
    membership = supabase.table("business_members") \
        .select("role") \
        .eq("user_id", user_id) \
        .eq("business_id", business_id) \
        .maybe_single() \
        .execute()

    if not membership.data:
        raise HTTPException(status_code=403, detail="Δεν έχεις πρόσβαση σε αυτό το business")

    dataset_id = str(uuid.uuid4())
    file_bytes = await file.read()
    filename_safe = file.filename.replace(" ", "_")   
    path = f"{business_id}/{dataset_id}_{filename_safe}"

    try:
        supabase.storage.from_("datasets").upload(
            path=path,
            file=file_bytes,
            file_options={"content-type": file.content_type or "application/octet-stream"}
        )
    except Exception as e:
        raise HTTPException(500, f"Αποτυχία upload: {str(e)}")


    new_dataset = {
        "id": dataset_id,
        "business_id": business_id,
        "name": file.filename,
        "storage_path": path,           
        "created_at": "now()"
    }

    inserted = supabase.table("datasets").insert(new_dataset).execute()

    if not inserted.data:
        raise HTTPException(500, "Αποτυχία αποθήκευσης metadata")

    return inserted.data[0]


@router.delete("/{dataset_id}")
async def delete_dataset(dataset_id: str, user_id: str = Depends(get_current_user)):
    dataset = supabase.table("datasets") \
        .select("business_id, storage_path") \
        .eq("id", dataset_id) \
        .eq("business_id", supabase.table("business_members").select("business_id").eq("user_id", user_id)) \
        .maybe_single() \
        .execute()

    if not dataset.data:
        raise HTTPException(403, "Δεν βρέθηκε ή δεν έχεις δικαίωμα")
    supabase.storage.from_("datasets").remove([dataset.data["storage_path"]])

    supabase.table("datasets").delete().eq("id", dataset_id).execute()

    return {"message": "Διαγράφηκε επιτυχώς"}


@router.patch("/{dataset_id}")
async def update_dataset(
    dataset_id: str,
    data: dict,  # {"name": "new name", ...}
    user_id: str = Depends(get_current_user)
):
    # Έλεγχος δικαιώματος
    dataset = supabase.table("datasets") \
        .select("business_id") \
        .eq("id", dataset_id) \
        .single() \
        .execute()

    if not dataset.data:
        raise HTTPException(404, "Dataset not found")

    membership = supabase.table("business_members") \
        .select("role") \
        .eq("user_id", user_id) \
        .eq("business_id", dataset.data["business_id"]) \
        .maybe_single() \
        .execute()

    if not membership.data:
        raise HTTPException(403, "Not allowed")

    # Update μόνο τα επιτρεπόμενα πεδία
    allowed_fields = ["name"]  # πρόσθεσε κι άλλα αν θες
    update_data = {k: v for k, v in data.items() if k in allowed_fields}

    if not update_data:
        raise HTTPException(400, "No valid fields to update")

    updated = supabase.table("datasets") \
        .update(update_data) \
        .eq("id", dataset_id) \
        .execute()

    if not updated.data:
        raise HTTPException(500, "Update failed")

    return updated.data[0]

@router.get("/signed-url/{dataset_id}")
async def get_signed_url(dataset_id: str, user_id: str = Depends(get_current_user)):
    dataset = supabase.table("datasets") \
        .select("storage_path, business_id") \
        .eq("id", dataset_id) \
        .single() \
        .execute()

    if not dataset.data:
        raise HTTPException(404)

    # Έλεγχος δικαιώματος
    membership = supabase.table("business_members") \
        .select("role") \
        .eq("user_id", user_id) \
        .eq("business_id", dataset.data["business_id"]) \
        .maybe_single() \
        .execute()

    if not membership.data:
        raise HTTPException(403)

    signed_url = supabase.storage.from_("datasets") \
        .create_signed_url(dataset.data["storage_path"], expires_in=3600)

    return {"signed_url": signed_url["signedURL"]}