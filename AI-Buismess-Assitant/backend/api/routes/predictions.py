"""
api/routes/predictions.py  –  Sales Forecast endpoint
──────────────────────────────────────────────────────
Χρησιμοποιεί το εκπαιδευμένο models/sales_model.pkl

Model features: date, sales + extra: temperature, promo, marketing_spend
Προσθήκη στο main.py:
    from api.routes import predictions
    app.include_router(predictions.router)
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from core.security import get_current_user
from db.supabase_client import supabase
import pandas as pd
import numpy as np
import joblib, io, os, uuid
from datetime import datetime

router = APIRouter(prefix="/api/predictions", tags=["Predictions"])

MODEL_PATH = os.environ.get("SALES_MODEL_PATH", "models/sales_model.pkl")
_artifact: dict | None = None


def get_artifact() -> dict:
    global _artifact
    if _artifact is None:
        if not os.path.exists(MODEL_PATH):
            raise HTTPException(503, f"Μοντέλο δεν βρέθηκε: '{MODEL_PATH}'. Αντίγραψε το sales_model.pkl στο models/")
        _artifact = joblib.load(MODEL_PATH)
    return _artifact


# ─── Feature engineering (ίδια λογική με train.py) ───────────────────────────

def _date_feats(df: pd.DataFrame, col: str) -> pd.DataFrame:
    df = df.copy()
    df[col] = pd.to_datetime(df[col], errors="coerce")
    df = df.dropna(subset=[col]).sort_values(col).reset_index(drop=True)
    df["day_of_week"]  = df[col].dt.dayofweek
    df["day_of_month"] = df[col].dt.day
    df["week_of_year"] = df[col].dt.isocalendar().week.astype(int)
    df["month"]        = df[col].dt.month
    df["quarter"]      = df[col].dt.quarter
    df["year"]         = df[col].dt.year
    df["is_weekend"]   = df["day_of_week"].isin([5, 6]).astype(int)
    df["is_month_end"] = df[col].dt.is_month_end.astype(int)
    return df


def _lag_feats(df: pd.DataFrame, target: str) -> pd.DataFrame:
    df = df.copy()
    for lag in [1, 3, 7, 14, 30]:
        df[f"lag_{lag}"] = df[target].shift(lag)
    df["rolling_mean_7"]  = df[target].shift(1).rolling(7).mean()
    df["rolling_mean_30"] = df[target].shift(1).rolling(30).mean()
    df["rolling_std_7"]   = df[target].shift(1).rolling(7).std()
    return df


def _predict_future(df: pd.DataFrame, artifact: dict, future_days: int, overrides: dict) -> list[dict]:
    date_col    = artifact["date_col"]
    target_col  = artifact["target_col"]
    extra_feats = artifact["extra_features"]   # ["temperature","promo","marketing_spend"]
    model       = artifact["model"]
    feat_names  = artifact["feature_names"]

    df = _date_feats(df, date_col)
    df = _lag_feats(df, target_col)
    df = df.dropna().reset_index(drop=True)

    if len(df) < 30:
        raise HTTPException(400, "Χρειάζονται τουλάχιστον 30 γραμμές για πρόβλεψη")

    last_date  = pd.to_datetime(df[date_col].max())
    last_sales = list(df[target_col].values[-30:])

    # Forward-fill: χρησιμοποιούμε τελευταίες γνωστές τιμές για extra features
    # Override με user-provided τιμές αν υπάρχουν
    extra_vals: dict[str, float] = {}
    for ef in extra_feats:
        val = overrides.get(ef)
        if val is not None:
            extra_vals[ef] = float(val)
        elif ef in df.columns:
            extra_vals[ef] = float(df[ef].iloc[-1])
        else:
            extra_vals[ef] = 0.0

    results = []
    for i in range(1, future_days + 1):
        fd = last_date + pd.Timedelta(days=i)
        row = {
            "day_of_week":  fd.dayofweek,
            "day_of_month": fd.day,
            "week_of_year": int(fd.isocalendar().week),
            "month":        fd.month,
            "quarter":      (fd.month - 1) // 3 + 1,
            "year":         fd.year,
            "is_weekend":   int(fd.dayofweek in [5, 6]),
            "is_month_end": int(fd.is_month_end),
            "lag_1":  last_sales[-1]  if len(last_sales) >= 1  else 0,
            "lag_3":  last_sales[-3]  if len(last_sales) >= 3  else 0,
            "lag_7":  last_sales[-7]  if len(last_sales) >= 7  else 0,
            "lag_14": last_sales[-14] if len(last_sales) >= 14 else 0,
            "lag_30": last_sales[-30] if len(last_sales) >= 30 else 0,
            "rolling_mean_7":  float(np.mean(last_sales[-7:])),
            "rolling_mean_30": float(np.mean(last_sales[-30:])),
            "rolling_std_7":   float(np.std(last_sales[-7:])),
            **extra_vals,
        }
        X    = pd.DataFrame([row])[feat_names]
        pred = max(0.0, float(model.predict(X)[0]))
        results.append({"date": fd.strftime("%Y-%m-%d"), "prediction": round(pred, 2)})
        last_sales.append(pred)

    return results


def _check_access(dataset_id: str, user_id: str) -> dict:
    biz_ids = [m["business_id"] for m in
               (supabase.table("business_members").select("business_id")
                .eq("user_id", user_id).execute().data or [])]
    ds = supabase.table("datasets").select("id, business_id, name, storage_path") \
        .eq("id", dataset_id).in_("business_id", biz_ids).maybe_single().execute()
    if not ds.data:
        raise HTTPException(403, "Dataset δεν βρέθηκε ή δεν έχεις πρόσβαση")
    return ds.data


# ─── Schemas ──────────────────────────────────────────────────────────────────

class PredictRequest(BaseModel):
    dataset_id:      str
    future_days:     int            = 30
    temperature:     Optional[float] = None   # override; αν None → forward-fill
    promo:           Optional[float] = None
    marketing_spend: Optional[float] = None


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/model-info")
async def model_info(_: str = Depends(get_current_user)):
    a = get_artifact()
    return {
        "status": "loaded",
        "date_col": a["date_col"],
        "target_col": a["target_col"],
        "extra_features": a["extra_features"],
        "n_features": len(a["feature_names"]),
    }


@router.get("")
async def list_predictions(
    dataset_id: Optional[str] = None,
    user_id: str = Depends(get_current_user),
):
    biz_ids = [m["business_id"] for m in
               (supabase.table("business_members").select("business_id")
                .eq("user_id", user_id).execute().data or [])]
    q = (supabase.table("predictions")
         .select("id, dataset_id, type, result, input_parameters, created_at")
         .in_("business_id", biz_ids)
         .order("created_at", desc=True))
    if dataset_id:
        q = q.eq("dataset_id", dataset_id)
    return q.execute().data or []


@router.post("/run")
async def run_prediction(body: PredictRequest, user_id: str = Depends(get_current_user)):
    ds       = _check_access(body.dataset_id, user_id)
    artifact = get_artifact()

    try:
        raw = supabase.storage.from_("datasets").download(ds["storage_path"])
        df  = pd.read_csv(io.StringIO(raw.decode("utf-8", errors="replace")))
    except Exception as e:
        raise HTTPException(500, f"Αδυναμία φόρτωσης αρχείου: {e}")

    required = [artifact["date_col"], artifact["target_col"]]
    missing  = [c for c in required if c not in df.columns]
    if missing:
        raise HTTPException(400, f"Λείπουν στήλες: {missing}. Βρέθηκαν: {list(df.columns)}")

    overrides = {}
    if body.temperature     is not None: overrides["temperature"]     = body.temperature
    if body.promo           is not None: overrides["promo"]           = body.promo
    if body.marketing_spend is not None: overrides["marketing_spend"] = body.marketing_spend

    results = _predict_future(df, artifact, body.future_days, overrides)

    values  = [r["prediction"] for r in results]
    peak    = max(results, key=lambda r: r["prediction"])
    summary = {
        "total":     round(sum(values), 2),
        "avg":       round(float(np.mean(values)), 2),
        "min":       round(float(np.min(values)), 2),
        "max":       round(float(np.max(values)), 2),
        "peak_date": peak["date"],
    }

    pred_id = str(uuid.uuid4())
    supabase.table("predictions").insert({
        "id":          pred_id,
        "business_id": ds["business_id"],
        "dataset_id":  body.dataset_id,
        "type":        "sales_forecast",
        "input_parameters": {"future_days": body.future_days, "overrides": overrides},
        "result": {"predictions": results, "summary": summary},
        "created_at": "now()",
    }).execute()

    return {
        "prediction_id":       pred_id,
        "dataset_name":        ds["name"],
        "future_days":         body.future_days,
        "results":             results,
        "summary":             summary,
        "extra_features_used": list(artifact["extra_features"]),
    }


@router.get("/{prediction_id}")
async def get_prediction(prediction_id: str, user_id: str = Depends(get_current_user)):
    biz_ids = [m["business_id"] for m in
               (supabase.table("business_members").select("business_id")
                .eq("user_id", user_id).execute().data or [])]
    pred = (supabase.table("predictions").select("*")
            .eq("id", prediction_id).in_("business_id", biz_ids)
            .maybe_single().execute())
    if not pred.data:
        raise HTTPException(404, "Prediction δεν βρέθηκε")
    return pred.data