import base64
import hashlib
import hmac
import json
from datetime import date, timedelta

from fastapi import FastAPI
from fastapi.testclient import TestClient

import api.routes.ai as ai_routes
import api.routes.integrations as integrations
import api.routes.products as products
import services.permissions as permissions
import services.stock as stock
from core.security import get_current_user
from services.forecasting import fit_series, forecast_days

BIZ, USER = "biz-1", "user-1"


def _app(monkeypatch, db, *routers):
    for mod in (permissions, stock, products, integrations):
        monkeypatch.setattr(mod, "supabase", db)
    db.tables["business_members"] = [{"user_id": USER, "business_id": BIZ, "role": "owner"}]
    app = FastAPI()
    for r in routers:
        app.include_router(r)
    app.dependency_overrides[get_current_user] = lambda: USER
    return TestClient(app)


# ── Forecasting ───────────────────────────────────────────────────────────────

def test_forecast_learns_level_and_weekday_pattern():
    start = date(2026, 1, 5)  # a Monday
    # 10/day on weekdays, 30 on Saturdays, 0 on Sundays, for 8 weeks
    series = {start + timedelta(days=i): [10, 10, 10, 10, 10, 30, 0][i % 7] for i in range(56)}
    level, factors, sd, n = fit_series(series, start, start + timedelta(days=55))
    assert n == 56
    assert 11 < level < 13                       # weekly mean is 80/7 ≈ 11.4
    assert factors[5] > 1.5 > factors[0] > factors[6]  # Saturday busiest, Sunday quietest
    week = forecast_days(level, factors, start + timedelta(days=56), 7)
    assert 70 < sum(week) < 95


def test_forecast_with_no_sales_is_zero():
    level, factors, sd, n = fit_series({}, date(2026, 1, 1), date(2026, 1, 31))
    assert level == 0 and sd == 0 and factors == [1.0] * 7


# ── Stock service (lots, FEFO) ────────────────────────────────────────────────

def test_outbound_consumes_earliest_expiring_lot_first(monkeypatch, fake_db):
    tables, db = fake_db
    monkeypatch.setattr(stock, "supabase", db)
    common = dict(business_id=BIZ, product_id="p1", user_id=USER)
    stock.apply_movement(type="inbound", quantity=10, lot_code="LATE", expiry_date="2027-01-01", **common)
    stock.apply_movement(type="inbound", quantity=5, lot_code="SOON", expiry_date="2026-11-01", **common)
    moved = stock.apply_movement(type="outbound", quantity=7, **common)

    lots = {l["lot_code"]: l["quantity"] for l in tables["inventory_lots"]}
    assert lots == {"SOON": 0, "LATE": 8}
    assert moved["new_quantity"] == 8
    assert [m["delta"] for m in tables["inventory_movements"]] == [10, 5, -7]


def test_adjustment_records_signed_delta(monkeypatch, fake_db):
    tables, db = fake_db
    monkeypatch.setattr(stock, "supabase", db)
    stock.apply_movement(business_id=BIZ, product_id="p1", type="inbound", quantity=20, user_id=USER)
    stock.apply_movement(business_id=BIZ, product_id="p1", type="adjustment", quantity=17, user_id=USER)
    assert tables["inventory_movements"][-1]["delta"] == -3
    assert tables["inventory_items"][0]["quantity"] == 17


# ── Product import ────────────────────────────────────────────────────────────

def test_import_creates_updates_and_sets_stock(monkeypatch, fake_db):
    tables, db = fake_db
    client = _app(monkeypatch, db, products.router)
    tables["products"] = [{"id": "p-old", "business_id": BIZ, "sku": "A-1", "name": "Old name"}]
    tables["inventory_items"] = [{"business_id": BIZ, "product_id": "p-old", "quantity": 3}]

    r = client.post("/api/products/import", json={"business_id": BIZ, "rows": [
        {"sku": "a-1", "name": "New name", "initial_stock": 12},
        {"sku": "B-2", "name": "Box", "barcode": "5201234567890", "initial_stock": 40},
        {"sku": "B-2", "name": "Box (fixed)", "initial_stock": 41},  # duplicate: last wins
    ]})
    assert r.status_code == 200, r.text
    assert r.json() == {"created": 1, "updated": 1, "skipped": 0}
    by_sku = {p["sku"]: p for p in tables["products"]}
    assert by_sku["A-1"]["name"] == "New name"
    assert by_sku["B-2"]["name"] == "Box (fixed)"
    qty = {i["product_id"]: i["quantity"] for i in tables["inventory_items"]}
    assert qty["p-old"] == 12 and qty[by_sku["B-2"]["id"]] == 41


# ── WooCommerce / Shopify webhooks ────────────────────────────────────────────

def _signed(secret: str, payload: dict) -> tuple[bytes, str]:
    body = json.dumps(payload).encode()
    return body, base64.b64encode(hmac.new(secret.encode(), body, hashlib.sha256).digest()).decode()


def test_woocommerce_order_reduces_stock_once(monkeypatch, fake_db):
    tables, db = fake_db
    client = _app(monkeypatch, db, integrations.router)
    tables["integrations"] = [{"id": "int-1", "business_id": BIZ, "provider": "woocommerce",
                               "secret": "s3cret-key", "enabled": True}]
    tables["products"] = [{"id": "p1", "business_id": BIZ, "sku": "TP-48"}]
    tables["inventory_items"] = [{"business_id": BIZ, "product_id": "p1", "quantity": 50}]
    payload = {"id": 991, "status": "processing", "billing": {"first_name": "Νίκος", "last_name": "Π."},
               "line_items": [{"sku": "TP-48", "quantity": 6, "price": 0.95}, {"sku": "NOPE", "quantity": 1}]}
    body, sig = _signed("s3cret-key", payload)
    headers = {"x-wc-webhook-topic": "order.updated", "x-wc-webhook-signature": sig,
               "content-type": "application/json"}

    first = client.post("/api/integrations/webhook/int-1", content=body, headers=headers)
    assert first.status_code == 200 and first.json()["matched"] == 1
    assert first.json()["unmatched"] == ["NOPE"]
    retry = client.post("/api/integrations/webhook/int-1", content=body, headers=headers)
    assert retry.json()["ignored"] == "duplicate"

    assert tables["inventory_items"][0]["quantity"] == 44
    assert len(tables["orders"]) == 1 and tables["orders"][0]["party_name"] == "Νίκος Π."


def test_webhook_rejects_bad_signature(monkeypatch, fake_db):
    tables, db = fake_db
    client = _app(monkeypatch, db, integrations.router)
    tables["integrations"] = [{"id": "int-1", "business_id": BIZ, "provider": "shopify",
                               "secret": "right-secret", "enabled": True}]
    body, sig = _signed("wrong-secret", {"id": 1, "line_items": []})
    r = client.post("/api/integrations/webhook/int-1", content=body, headers={"x-shopify-hmac-sha256": sig})
    assert r.status_code == 401


# ── Invoice line matching ─────────────────────────────────────────────────────

def test_invoice_lines_match_by_code_barcode_and_name():
    catalog = [
        {"id": "1", "sku": "CB-4030", "name": "Χαρτοκούτι 40×30×30", "barcode": None},
        {"id": "2", "sku": "TP-48", "name": "Ταινία συσκευασίας 48mm", "barcode": "5201111111111"},
        {"id": "3", "sku": "GL-NIT", "name": "Γάντια νιτριλίου M", "barcode": None},
    ]
    line = lambda **kw: ai_routes.InvoiceLine(**{"description": "", "code": None, "barcode": None, "quantity": 1,
                                                 "unit": None, "unit_price": None, "line_total": None, **kw})
    out = ai_routes._match([
        line(description="ΚΟΥΤΙ", code="cb-4030"),
        line(description="Ταινία", barcode="5201111111111"),
        line(description="ΓΑΝΤΙΑ ΝΙΤΡΙΛΙΟΥ Μ"),
        line(description="Κάτι εντελώς άσχετο 123"),
    ], catalog)
    assert [o["match"] and o["match"]["product_id"] for o in out] == ["1", "2", "3", None]
    assert [o["match"]["by"] for o in out[:3]] == ["sku", "barcode", "name"]
