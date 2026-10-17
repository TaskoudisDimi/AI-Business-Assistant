from fastapi import FastAPI
from fastapi.testclient import TestClient

import api.routes.products as products
import services.permissions as permissions
from core.security import get_current_user


def _client(monkeypatch, fake_db, user_id):
    tables, client = fake_db
    monkeypatch.setattr(permissions, "supabase", client)
    monkeypatch.setattr(products, "supabase", client)
    app = FastAPI()
    app.include_router(products.router)
    app.dependency_overrides[get_current_user] = lambda: user_id
    return tables, TestClient(app)


def test_member_can_list_products(monkeypatch, fake_db):
    # Regression: the access check was once called with (business_id, user_id)
    # swapped, so every member got 403.
    tables, client = _client(monkeypatch, fake_db, "user-1")
    tables["business_members"] = [{"id": "m1", "user_id": "user-1", "business_id": "biz-1", "role": "owner"}]
    tables["products"] = [{"id": "p1", "business_id": "biz-1", "sku": "A"}]

    r = client.get("/api/products", params={"business_id": "biz-1"})
    assert r.status_code == 200
    assert [p["id"] for p in r.json()] == ["p1"]


def test_non_member_gets_403(monkeypatch, fake_db):
    tables, client = _client(monkeypatch, fake_db, "user-2")
    tables["business_members"] = [{"id": "m1", "user_id": "user-1", "business_id": "biz-1", "role": "owner"}]

    r = client.get("/api/products", params={"business_id": "biz-1"})
    assert r.status_code == 403
