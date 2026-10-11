from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone
from core.security import get_current_user
from db.supabase_client import supabase

router = APIRouter(prefix="/api/customers", tags=["Customers"])


def _check_biz(business_id: str, user_id: str):
    m = supabase.table("business_members") \
        .select("role").eq("user_id", user_id).eq("business_id", business_id) \
        .maybe_single().execute()
    if not m.data:
        raise HTTPException(403, "Access denied")


def _segment(total_orders: int, total_revenue: float, days_since: int, avg_revenue: float) -> str:
    if days_since > 90 and total_orders > 2:
        return "dormant"
    if days_since > 60 and total_orders > 2:
        return "at_risk"
    if total_orders <= 2:
        return "new"
    if total_revenue >= avg_revenue * 1.5 and total_orders >= 3:
        return "high_value"
    return "loyal"


@router.get("/analysis")
async def customer_analysis(business_id: str, user_id: str = Depends(get_current_user)):
    _check_biz(business_id, user_id)

    # Fetch all completed sale orders
    orders_res = supabase.table("orders") \
        .select("id, party_name, created_at, status") \
        .eq("business_id", business_id) \
        .eq("type", "sale") \
        .eq("status", "completed") \
        .execute()

    orders = orders_res.data or []
    if not orders:
        return {
            "summary": {"total_customers": 0, "total_revenue": 0, "avg_order_value": 0, "at_risk_count": 0},
            "customers": [],
            "segments": {"high_value": 0, "loyal": 0, "at_risk": 0, "new": 0, "dormant": 0},
            "top_products": [],
        }

    order_ids = [o["id"] for o in orders]

    # Fetch all order items for these orders
    items_res = supabase.table("order_items") \
        .select("order_id, product_id, quantity, unit_price, products(sku, name)") \
        .in_("order_id", order_ids) \
        .execute()

    items = items_res.data or []

    # Build revenue map per order
    revenue_by_order: dict = {}
    product_sales: dict = {}  # product_id → {sku, name, total_qty, total_rev}

    for item in items:
        oid = item["order_id"]
        qty = item.get("quantity", 0)
        price = item.get("unit_price") or 0
        line_rev = qty * price
        revenue_by_order[oid] = revenue_by_order.get(oid, 0) + line_rev

        pid = item.get("product_id")
        if pid:
            p = item.get("products") or {}
            if pid not in product_sales:
                product_sales[pid] = {"sku": p.get("sku", ""), "name": p.get("name", ""), "total_qty": 0, "total_revenue": 0}
            product_sales[pid]["total_qty"] += qty
            product_sales[pid]["total_revenue"] += line_rev

    # Aggregate per customer (party_name)
    now = datetime.now(timezone.utc)
    customer_map: dict = {}

    for order in orders:
        name = order.get("party_name") or "Unknown"
        created_at = order["created_at"]
        try:
            order_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        except Exception:
            order_dt = now

        rev = revenue_by_order.get(order["id"], 0)

        if name not in customer_map:
            customer_map[name] = {
                "name": name,
                "total_orders": 0,
                "total_revenue": 0.0,
                "last_order_date": order_dt,
                "first_order_date": order_dt,
            }

        c = customer_map[name]
        c["total_orders"] += 1
        c["total_revenue"] += rev
        if order_dt > c["last_order_date"]:
            c["last_order_date"] = order_dt
        if order_dt < c["first_order_date"]:
            c["first_order_date"] = order_dt

    # Calculate metrics
    customers = []
    total_revenue_all = sum(c["total_revenue"] for c in customer_map.values())
    avg_revenue = total_revenue_all / len(customer_map) if customer_map else 0

    for c in customer_map.values():
        days_since = (now - c["last_order_date"]).days
        avg_order_value = c["total_revenue"] / c["total_orders"] if c["total_orders"] > 0 else 0
        segment = _segment(c["total_orders"], c["total_revenue"], days_since, avg_revenue)

        customers.append({
            "name": c["name"],
            "total_orders": c["total_orders"],
            "total_revenue": round(c["total_revenue"], 2),
            "avg_order_value": round(avg_order_value, 2),
            "days_since_last_order": days_since,
            "last_order_date": c["last_order_date"].strftime("%Y-%m-%d"),
            "first_order_date": c["first_order_date"].strftime("%Y-%m-%d"),
            "segment": segment,
        })

    customers.sort(key=lambda x: x["total_revenue"], reverse=True)

    # Segment counts
    seg_counts = {"high_value": 0, "loyal": 0, "at_risk": 0, "new": 0, "dormant": 0}
    for c in customers:
        seg_counts[c["segment"]] = seg_counts.get(c["segment"], 0) + 1

    at_risk_count = seg_counts["at_risk"] + seg_counts["dormant"]

    # Top products by quantity sold
    top_products = sorted(product_sales.values(), key=lambda x: x["total_qty"], reverse=True)[:8]

    return {
        "summary": {
            "total_customers": len(customers),
            "total_revenue": round(total_revenue_all, 2),
            "avg_order_value": round(total_revenue_all / len(orders), 2) if orders else 0,
            "at_risk_count": at_risk_count,
        },
        "customers": customers,
        "segments": seg_counts,
        "top_products": [
            {"sku": p["sku"], "name": p["name"], "total_qty": p["total_qty"], "total_revenue": round(p["total_revenue"], 2)}
            for p in top_products
        ],
    }
