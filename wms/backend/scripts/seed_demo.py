"""
Fill a business with realistic demo data: products, stock, ~4 months of purchase and
sale orders, stock movements and customers. Useful for testing every screen and for
recording a product video.

Everything it creates is tagged (SKU prefix "DEMO-", order notes "demo-seed"), so
--clean removes exactly that and nothing else.

    cd wms/backend
    venv/bin/python scripts/seed_demo.py --email you@example.com          # first business of that user
    venv/bin/python scripts/seed_demo.py --business-id <uuid>
    venv/bin/python scripts/seed_demo.py --email you@example.com --clean  # remove demo data

Uses SUPABASE_URL / SUPABASE_KEY from backend/.env (service role).
"""
import argparse
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from db.supabase_client import supabase  # noqa: E402

TAG = "demo-seed"
SKU_PREFIX = "DEMO-"

# sku, name, category, unit, cost, price, reorder point, avg units sold per day
PRODUCTS = [
    ("CB-4030", "Χαρτοκούτι 40×30×30",        "Συσκευασία", "τεμ",  0.62,  1.10, 200, 38),
    ("CB-6040", "Χαρτοκούτι 60×40×40",        "Συσκευασία", "τεμ",  0.95,  1.70, 120, 18),
    ("PW-023",  "Stretch film 23μm",          "Συσκευασία", "ρολό", 6.40, 11.50,  40,  9),
    ("TP-48",   "Ταινία συσκευασίας 48mm",    "Συσκευασία", "τεμ",  0.48,  0.95, 150, 31),
    ("BW-100",  "Αφρώδες περιτύλιγμα 100m",   "Συσκευασία", "ρολό", 9.80, 17.90,  15,  2),
    ("LB-A6",   "Θερμικές ετικέτες A6 (500)", "Ετικέτες",   "ρολό", 3.10,  5.90,  60, 11),
    ("LB-A4",   "Ετικέτες A4 αυτοκόλλητες",   "Ετικέτες",   "πακ",  4.20,  7.80,  25,  3),
    ("PL-EUR",  "Παλέτα EUR 120×80",          "Παλέτες",    "τεμ",  9.50, 14.00,  20,  4),
    ("GL-NIT",  "Γάντια νιτριλίου M (100)",   "Αναλώσιμα",  "κουτί",3.90,  6.90,  30,  6),
    ("CT-KNF",  "Κοπίδι ασφαλείας",           "Εργαλεία",   "τεμ",  2.10,  4.50,  10,  1),
    ("MK-BLK",  "Μαρκαδόροι ανεξίτηλοι (12)", "Αναλώσιμα",  "πακ",  3.30,  6.20,  12,  1),
    ("ST-PLS",  "Ιμάντας δεσίματος PP 12mm",  "Συσκευασία", "ρολό", 14.0, 24.00,   8,  1),
]

# name, orders per month, basket size multiplier, days since their last order (drives RFM)
CUSTOMERS = [
    ("Κρητικός ΑΕ",              9, 2.2,  2),
    ("Logistics Βορείου ΙΚΕ",    7, 1.8,  5),
    ("Παπαδόπουλος & Σια ΟΕ",    5, 1.0,  9),
    ("Agro Trade Θεσσαλίας",     4, 1.4, 70),   # at risk
    ("Delta Pack",               3, 0.8, 12),
    ("Ηλίας Μάρκου – e-shop",    6, 0.6,  1),
    ("Κάβα Αιγαίο",            0.5, 0.7,  4),   # new: only 2 orders
    ("Βιοτεχνία Σταμάτη",        3, 1.1, 100),  # dormant
]
SUPPLIERS = ["Χαρτοποιία Αττικής ΑΕ", "PackPro Hellas", "Euro Pallets ΕΠΕ"]
DAYS = 120


def find_business(email: str | None, business_id: str | None) -> tuple[str, str]:
    if business_id:
        biz = supabase.table("businesses").select("id, owner_id").eq("id", business_id).maybe_single().execute()
        if not biz:
            sys.exit(f"Business {business_id} not found")
        return biz.data["id"], biz.data["owner_id"]
    users = supabase.auth.admin.list_users(per_page=1000)
    user = next((u for u in users if (u.email or "").lower() == email.lower()), None)
    if not user:
        sys.exit(f"No user with email {email}")
    m = supabase.table("business_members").select("business_id").eq("user_id", user.id).limit(1).execute()
    if not m.data:
        sys.exit(f"{email} has no business yet — sign in once so one is created")
    return m.data[0]["business_id"], user.id


def clean(business_id: str) -> None:
    supabase.table("orders").delete().eq("business_id", business_id).eq("notes", TAG).execute()
    supabase.table("products").delete().eq("business_id", business_id).like("sku", f"{SKU_PREFIX}%").execute()
    print("Removed demo products, orders, stock and movements.")


def seed(business_id: str, user_id: str) -> None:
    rnd = random.Random(7)
    now = datetime.now(timezone.utc)

    products = supabase.table("products").insert([{
        "business_id": business_id, "sku": SKU_PREFIX + sku, "name": name, "category": cat, "unit": unit,
        "cost_price": cost, "sell_price": price, "reorder_point": rp,
    } for sku, name, cat, unit, cost, price, rp, _ in PRODUCTS]).execute().data
    by_sku = {p["sku"][len(SKU_PREFIX):]: p for p in products}
    stock = {p["id"]: 0 for p in products}
    print(f"Created {len(products)} products")

    orders, items_by_order, movements = [], {}, []

    def add_order(kind: str, party: str, when: datetime, lines: list[tuple[dict, int, float]], status="completed"):
        order = {"business_id": business_id, "type": kind, "status": status, "party_name": party,
                 "notes": TAG, "created_by": user_id, "created_at": when.isoformat()}
        orders.append(order)
        items_by_order[id(order)] = lines
        if status != "completed":
            return
        for prod, qty, _ in lines:
            stock[prod["id"]] += qty if kind == "purchase" else -qty
            movements.append((order, {
                "product_id": prod["id"], "business_id": business_id,
                "type": "inbound" if kind == "purchase" else "outbound", "quantity": qty,
                "reason": f"Order ({party})", "created_by": user_id, "created_at": when.isoformat(),
            }))

    # 1. Sales: each customer orders regularly up to their "last order" date
    sales = []  # (days_ago, party, lines)
    for name, per_month, basket, last_gap in CUSTOMERS:
        n = max(1, round(per_month * DAYS / 30))
        for k in range(n):
            # spread orders evenly between DAYS ago and their most recent order
            days_ago = last_gap + int((DAYS - last_gap) * k / max(n - 1, 1)) if n > 1 else last_gap
            lines = []
            for s, _, _, _, _, price, _, rate in rnd.sample(PRODUCTS, k=rnd.randint(2, 5)):
                qty = max(1, int(rnd.gauss(rate * 3.5 * basket, rate * 0.8)))
                lines.append((by_sku[s], qty, price))
            sales.append((days_ago, name, lines))

    sold_total = {p["id"]: 0 for p in products}
    sold_30d = {p["id"]: 0 for p in products}
    sold_in = lambda pid, lo, hi: sum(q for d, _, ls in sales for pr, q, _ in ls if pr["id"] == pid and lo <= d < hi)
    for days_ago, _, lines in sales:
        for prod, qty, _ in lines:
            sold_total[prod["id"]] += qty
            if days_ago < 30:
                sold_30d[prod["id"]] += qty

    # 2. Where each product should end up, in days of cover (drives the reorder alerts)
    cover_days = {"PW-023": 2, "TP-48": 4, "PL-EUR": 5,   # critical
                  "GL-NIT": 9, "LB-A6": 12}               # warning
    target = {}
    for sku, *_rest in PRODUCTS:
        pid, rp = by_sku[sku]["id"], by_sku[sku]["reorder_point"]
        daily = sold_30d[pid] / 30
        days = cover_days.get(sku, rnd.randint(25, 50))
        target[pid] = max(1, round(daily * days)) if sku in cover_days else max(rp + 5, round(daily * days))

    # 3. Restocks every 3 weeks replace what sold in the previous 3 weeks; the low
    #    products miss the last two restocks, which is why they are running out
    restocks = []
    for k in range(1, DAYS // 21 + 1):
        days_ago = DAYS - 21 * k
        lines = [(by_sku[s], sold_in(by_sku[s]["id"], days_ago, days_ago + 21), cost)
                 for s, _, _, _, cost, _, _, _ in PRODUCTS
                 if not (s in cover_days and days_ago < 45)]
        restocks.append((days_ago, SUPPLIERS[k % len(SUPPLIERS)], [l for l in lines if l[1] > 0]))
    restocked = {p["id"]: 0 for p in products}
    for _, _, lines in restocks:
        for prod, qty, _ in lines:
            restocked[prod["id"]] += qty

    # 4. Opening stock makes the numbers add up: opening + restocks - sales = target
    opening = [(prod, max(target[prod["id"]] + sold_total[prod["id"]] - restocked[prod["id"]], 0), cost)
               for prod, (_, _, _, _, cost, *_r) in zip(products, PRODUCTS)]
    add_order("purchase", SUPPLIERS[0], now - timedelta(days=DAYS + 1), opening)

    events = [(d, "purchase", party, lines) for d, party, lines in restocks] + \
             [(d, "sale", party, lines) for d, party, lines in sales]
    for days_ago, kind, party, lines in sorted(events, key=lambda e: -e[0]):
        when = now - timedelta(days=days_ago, hours=rnd.randint(1, 9), minutes=rnd.randint(0, 59))
        add_order(kind, party, when, lines)

    # A few open orders so every status shows up
    add_order("sale", "Παπαδόπουλος & Σια ΟΕ", now - timedelta(hours=5), [(by_sku["CB-4030"], 80, 1.10)], status="confirmed")
    add_order("sale", "Delta Pack", now - timedelta(hours=1), [(by_sku["LB-A6"], 10, 5.90)], status="draft")
    add_order("purchase", "PackPro Hellas", now - timedelta(days=1), [(by_sku["PW-023"], 60, 6.40)], status="confirmed")
    add_order("sale", "Κάβα Αιγαίο", now - timedelta(days=6), [(by_sku["GL-NIT"], 4, 6.90)], status="cancelled")

    # Insert orders in chunks and map them back by position
    created = []
    for i in range(0, len(orders), 200):
        created += supabase.table("orders").insert(orders[i:i + 200]).execute().data
    ids = {id(o): c["id"] for o, c in zip(orders, created)}

    items = [{"order_id": ids[id(o)], "product_id": p["id"], "quantity": q, "unit_price": price}
             for o in orders for p, q, price in items_by_order[id(o)]]
    for i in range(0, len(items), 500):
        supabase.table("order_items").insert(items[i:i + 500]).execute()

    moves = [{**m, "order_id": ids[id(o)]} for o, m in movements]
    for i in range(0, len(moves), 500):
        supabase.table("inventory_movements").insert(moves[i:i + 500]).execute()

    supabase.table("inventory_items").insert([{
        "product_id": pid, "business_id": business_id, "quantity": max(qty, 0), "last_updated": now.isoformat(),
    } for pid, qty in stock.items()]).execute()

    print(f"Created {len(orders)} orders, {len(items)} order lines, {len(moves)} stock movements")
    low = [p["name"] for p in products if stock[p["id"]] <= p["reorder_point"]]
    print(f"Products at/below reorder point: {', '.join(low) or 'none'}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    who = ap.add_mutually_exclusive_group(required=True)
    who.add_argument("--email", help="seed the first business of this user")
    who.add_argument("--business-id", help="seed this business")
    ap.add_argument("--clean", action="store_true", help="remove previously seeded demo data and exit")
    args = ap.parse_args()

    biz_id, owner_id = find_business(args.email, args.business_id)
    clean(biz_id)
    if not args.clean:
        seed(biz_id, owner_id)
