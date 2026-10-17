import time
from types import SimpleNamespace as NS

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

import api.routes.auth as auth
import core.middleware as mw
from tests.conftest import make_jwt


# ── Session refresh middleware ────────────────────────────────────────────────

def _app_with_refresh(monkeypatch, new_access):
    monkeypatch.setattr(mw, "new_auth_client", lambda: NS(auth=NS(
        refresh_session=lambda rt: NS(session=NS(access_token=new_access, refresh_token="r2")))))
    app = FastAPI()
    app.add_middleware(mw.RefreshSessionMiddleware)

    @app.get("/x")
    def x(request: Request):
        return {"tok": request.cookies.get("access_token")}

    return TestClient(app)


def test_expired_token_is_refreshed_before_the_handler_runs(monkeypatch):
    fresh = make_jwt({"exp": time.time() + 3600})
    client = _app_with_refresh(monkeypatch, fresh)
    r = client.get("/x", cookies={"access_token": make_jwt({"exp": time.time() - 10}), "refresh_token": "r1"})
    assert r.json()["tok"] == fresh
    assert "r2" in r.headers["set-cookie"]


def test_valid_token_is_left_alone(monkeypatch):
    fresh = make_jwt({"exp": time.time() + 3600})
    client = _app_with_refresh(monkeypatch, "unused")
    r = client.get("/x", cookies={"access_token": fresh, "refresh_token": "r1"})
    assert r.json()["tok"] == fresh
    assert "set-cookie" not in r.headers


# ── Password reset ────────────────────────────────────────────────────────────

def _reset_client(monkeypatch):
    updated = []
    monkeypatch.setattr(auth, "supabase", NS(auth=NS(
        get_user=lambda t: NS(user=NS(id="u1")),
        admin=NS(update_user_by_id=lambda uid, d: updated.append(uid)),
    )))
    app = FastAPI()
    app.include_router(auth.router)
    return TestClient(app), updated


def _reset(client, amr):
    return client.post("/api/auth/reset-password",
                       json={"password": "newpassword1", "access_token": make_jwt({"amr": amr})})


def test_reset_accepts_fresh_email_link_session(monkeypatch):
    client, updated = _reset_client(monkeypatch)
    assert _reset(client, [{"method": "otp", "timestamp": time.time() - 60}]).status_code == 200
    assert _reset(client, [{"method": "recovery", "timestamp": time.time() - 60}]).status_code == 200
    assert updated == ["u1", "u1"]


def test_reset_rejects_password_login_session(monkeypatch):
    client, updated = _reset_client(monkeypatch)
    assert _reset(client, [{"method": "password", "timestamp": time.time()}]).status_code == 400
    assert updated == []


def test_reset_rejects_old_link(monkeypatch):
    client, updated = _reset_client(monkeypatch)
    assert _reset(client, [{"method": "otp", "timestamp": time.time() - 7200}]).status_code == 400
    assert updated == []


def test_reset_requires_min_password_length(monkeypatch):
    client, _ = _reset_client(monkeypatch)
    r = client.post("/api/auth/reset-password", json={"password": "short", "access_token": "x"})
    assert r.status_code == 422
