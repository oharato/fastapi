from fastapi.testclient import TestClient

from tests.conftest import make_auth_headers


# ─── ログイン ───────────────────────────────────────────────────────────────

def test_login_成功(raw_client: TestClient, test_user):
    res = raw_client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "test"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_パスワード不正(raw_client: TestClient, test_user):
    res = raw_client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "wrong"},
    )
    assert res.status_code == 401


def test_login_存在しないユーザー(raw_client: TestClient):
    res = raw_client.post(
        "/api/auth/login",
        json={"email": "nobody@example.com", "password": "test"},
    )
    assert res.status_code == 401


# ─── /api/auth/me ────────────────────────────────────────────────────────────

def test_me_認証済みユーザーを返す(raw_client: TestClient, test_user):
    headers = make_auth_headers(test_user)
    res = raw_client.get("/api/auth/me", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["email"] == "test@example.com"
    assert data["id"] == test_user.id
    assert "hashed_password" not in data


def test_me_トークンなしは401(raw_client: TestClient):
    res = raw_client.get("/api/auth/me")
    assert res.status_code == 401


def test_me_不正なトークンは401(raw_client: TestClient):
    res = raw_client.get("/api/auth/me", headers={"Authorization": "Bearer invalid"})
    assert res.status_code == 401


# ─── 認証保護されたエンドポイント ──────────────────────────────────────────

def test_todos_トークンなしは401(raw_client: TestClient):
    res = raw_client.get("/api/todos")
    assert res.status_code == 401


def test_jobs_トークンなしは401(raw_client: TestClient):
    res = raw_client.get("/api/jobs")
    assert res.status_code == 401


def test_無効トークンでtodoアクセスは401(raw_client: TestClient):
    res = raw_client.get("/api/todos", headers={"Authorization": "Bearer bad.token.here"})
    assert res.status_code == 401
