from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from core.security import get_current_user
from db.supabase_client import supabase
import uuid
from pydantic import BaseModel
import csv, io

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

    res = supabase.storage.from_("datasets").upload(
    path=path,
    file=file_bytes,
    file_options={"content-type": file.content_type or "application/octet-stream"}
)
    if hasattr(res, "error") and res.error:
        raise HTTPException(500, f"Upload error: {res.error}")


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
    memberships = supabase.table("business_members") \
    .select("business_id") \
    .eq("user_id", user_id) \
    .execute()

    business_ids = [m["business_id"] for m in memberships.data]

    dataset = supabase.table("datasets") \
        .select("business_id, storage_path") \
        .eq("id", dataset_id) \
        .in_("business_id", business_ids) \
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



def _check_access(dataset_id: str, user_id: str) -> dict:
    """Επιστρέφει το dataset row αν ο user έχει πρόσβαση, αλλιώς 403."""
    memberships = supabase.table("business_members") \
        .select("business_id") \
        .eq("user_id", user_id) \
        .execute()
 
    business_ids = [m["business_id"] for m in (memberships.data or [])]
 
    dataset = supabase.table("datasets") \
        .select("id, business_id, name, storage_path, columns") \
        .eq("id", dataset_id) \
        .in_("business_id", business_ids) \
        .maybe_single() \
        .execute()
 
    if not dataset.data:
        raise HTTPException(403, "Δεν βρέθηκε ή δεν έχεις πρόσβαση")
 
    return dataset.data
 
 
def _download_csv(storage_path: str) -> str:
    """Κατεβάζει το αρχείο από Supabase Storage και επιστρέφει το περιεχόμενο."""
    res = supabase.storage.from_("datasets").download(storage_path)
    # res είναι bytes
    return res.decode("utf-8", errors="replace")
 
 
def _parse_csv(content: str) -> tuple[list[str], list[dict]]:
    reader = csv.DictReader(io.StringIO(content))
    columns = reader.fieldnames or []
    rows = [dict(r) for r in reader]
    return list(columns), rows
 
 
def _rows_to_csv(columns: list[str], rows: list[dict]) -> str:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=columns, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()
 
 
# ─── GET /datasets/{dataset_id}/rows ──────────────────────────────────────────
 
@router.get("/{dataset_id}/rows")
async def get_dataset_rows(
    dataset_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Επιστρέφει { columns: [...], rows: [...] } από το CSV αρχείο.
    Αν έχουν ήδη αποθηκευτεί columns στη DB τα χρησιμοποιεί για metadata,
    αλλά τα rows τα διαβάζει πάντα από το storage.
    """
    ds = _check_access(dataset_id, user_id)
 
    try:
        content = _download_csv(ds["storage_path"])
    except Exception as e:
        raise HTTPException(500, f"Αδυναμία λήψης αρχείου: {e}")
 
    columns, rows = _parse_csv(content)
 
    # Αποθήκευσε columns στη DB αν δεν υπάρχουν ήδη
    if not ds.get("columns") and columns:
        supabase.table("datasets") \
            .update({"columns": columns, "rows_count": len(rows)}) \
            .eq("id", dataset_id) \
            .execute()
 
    return {"columns": columns, "rows": rows, "total": len(rows)}
 
 
# ─── PATCH /datasets/{dataset_id}/rows ────────────────────────────────────────
 
class RowChange(BaseModel):
    index: int          # global 0-based index στο αρχείο
    row: dict           # updated row data
 
 
class SaveChangesRequest(BaseModel):
    changes: list[RowChange]
 
 
@router.patch("/{dataset_id}/rows")
async def save_dataset_rows(
    dataset_id: str,
    body: SaveChangesRequest,
    user_id: str = Depends(get_current_user)
):
    """
    Εφαρμόζει τις αλλαγές και ανεβάζει το ενημερωμένο CSV πίσω στο Storage.
    """
    ds = _check_access(dataset_id, user_id)
 
    # 1. Κατέβασε το τρέχον CSV
    try:
        content = _download_csv(ds["storage_path"])
    except Exception as e:
        raise HTTPException(500, f"Αδυναμία λήψης αρχείου: {e}")
 
    columns, rows = _parse_csv(content)
 
    # 2. Εφάρμοσε αλλαγές
    for change in body.changes:
        if 0 <= change.index < len(rows):
            rows[change.index] = change.row
 
    # 3. Ξαναφτιάξε CSV
    updated_csv = _rows_to_csv(columns, rows)
 
    # 4. Ανέβασε πίσω (overwrite)
    try:
        supabase.storage.from_("datasets").update(
            path=ds["storage_path"],
            file=updated_csv.encode("utf-8"),
            file_options={"content-type": "text/csv"}
        )
    except Exception as e:
        raise HTTPException(500, f"Αποτυχία αποθήκευσης: {e}")
 
    # 5. Ενημέρωσε rows_count αν άλλαξε
    supabase.table("datasets") \
        .update({"rows_count": len(rows)}) \
        .eq("id", dataset_id) \
        .execute()
 
    return {"message": "Αποθηκεύτηκε", "rows_count": len(rows)}
 