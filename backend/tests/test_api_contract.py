"""app/api/deps.py 的接口契约：登录鉴权、权限校验、分页参数。

不连接 MySQL / Redis：用 dependency_overrides 覆盖 get_db 与 get_current_user，
用 monkeypatch 替换 deps 模块内的 get_user / get_user_permissions（二者都在调用期按模块全局名查找）。
"""

import pytest
from app.api.deps import get_current_user, require_permission
from app.core.security import create_access_token
from app.db.session import get_db


@pytest.fixture
def dummy_db(app):
    app.dependency_overrides[get_db] = lambda: None


def auth_header(username="tester"):
    return {"Authorization": f"Bearer {create_access_token(username)}"}


# ---------- 登录鉴权 ----------

def test_missing_token_is_401(client):
    resp = client.get("/need-login")
    assert resp.status_code == 401
    assert resp.json() == {"code": 401, "message": "Not authenticated", "data": None}


def test_malformed_token_is_401(client):
    resp = client.get("/need-login", headers={"Authorization": "Bearer not-a-jwt"})
    assert resp.status_code == 401
    assert resp.json()["message"] == "token 无效或已过期"


def test_valid_token_resolves_existing_user(client, dummy_db, fake_user, monkeypatch):
    seen = {}

    def fake_get_user(db, username):
        seen["username"] = username
        return fake_user

    monkeypatch.setattr("app.api.deps.get_user", fake_get_user)
    resp = client.get("/need-login", headers=auth_header("tester"))
    assert resp.status_code == 200
    assert resp.json()["data"] == "tester"
    assert seen["username"] == "tester"


def test_valid_token_for_unknown_user_is_401(client, dummy_db, monkeypatch):
    monkeypatch.setattr("app.api.deps.get_user", lambda db, username: None)
    resp = client.get("/need-login", headers=auth_header("ghost"))
    assert resp.status_code == 401
    assert resp.json()["message"] == "用户不存在"


def test_token_signed_with_other_key_is_401(client):
    from jose import jwt

    forged = jwt.encode({"sub": "admin"}, "not-the-real-secret", algorithm="HS256")
    resp = client.get("/need-login", headers={"Authorization": f"Bearer {forged}"})
    assert resp.status_code == 401


# ---------- 权限校验 ----------

def test_permission_granted_returns_current_user(client, app, dummy_db, fake_user, monkeypatch):
    app.dependency_overrides[get_current_user] = lambda: fake_user
    monkeypatch.setattr("app.api.deps.get_user_permissions", lambda db, user_id: ["dashboard:read"])
    resp = client.get("/need-permission")
    assert resp.status_code == 200
    assert resp.json() == {"code": 0, "message": "success", "data": "tester"}


def test_permission_missing_is_403(client, app, dummy_db, fake_user, monkeypatch):
    app.dependency_overrides[get_current_user] = lambda: fake_user
    monkeypatch.setattr("app.api.deps.get_user_permissions", lambda db, user_id: ["order:read"])
    resp = client.get("/need-permission")
    assert resp.status_code == 403
    assert resp.json() == {"code": 403, "message": "没有权限执行此操作", "data": None}


def test_permission_empty_list_is_403(client, app, dummy_db, fake_user, monkeypatch):
    app.dependency_overrides[get_current_user] = lambda: fake_user
    monkeypatch.setattr("app.api.deps.get_user_permissions", lambda db, user_id: [])
    assert client.get("/need-permission").status_code == 403


def test_permission_check_runs_after_login(client):
    """未登录时先被 get_current_user 拦下（401），而不是直接 403。"""
    assert client.get("/need-permission").status_code == 401


def test_permission_is_checked_by_exact_name(client, app, dummy_db, fake_user, monkeypatch):
    """前缀相同的其他权限不应放行。"""
    app.dependency_overrides[get_current_user] = lambda: fake_user
    monkeypatch.setattr("app.api.deps.get_user_permissions", lambda db, user_id: ["dashboard:write"])
    assert client.get("/need-permission").status_code == 403


def test_require_permission_returns_independent_closures():
    assert require_permission("a:read") is not require_permission("a:read")


# ---------- 分页参数 ----------

def test_page_defaults(client):
    assert client.get("/page").json()["data"] == {"page": 1, "page_size": 20, "offset": 0, "limit": 20}


def test_page_computes_offset_and_limit(client):
    data = client.get("/page", params={"page": 3, "page_size": 10}).json()["data"]
    assert data == {"page": 3, "page_size": 10, "offset": 20, "limit": 10}


def test_page_size_upper_bound_is_100(client):
    assert client.get("/page", params={"page_size": 100}).status_code == 200
    resp = client.get("/page", params={"page_size": 101})
    assert resp.status_code == 422
    assert resp.json() == {"code": 422, "message": "参数校验失败", "data": None}


@pytest.mark.parametrize("params", [{"page": 0}, {"page": -1}, {"page_size": 0}, {"page_size": -5}, {"page": "abc"}])
def test_invalid_page_params_are_422(client, params):
    resp = client.get("/page", params=params)
    assert resp.status_code == 422
    assert resp.json()["code"] == 422