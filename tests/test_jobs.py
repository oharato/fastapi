from unittest.mock import AsyncMock, patch
import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.user import User
from app.schemas.job import JobCreate
from app.services import job as job_svc
from app.tasks.sample import run_sample_job
from tests.conftest import make_auth_headers


# ─── ジョブ一覧 ─────────────────────────────────────────────────────────────

def test_job_一覧_初期は空(client: TestClient):
    res = client.get("/api/jobs")
    assert res.status_code == 200
    assert res.json() == []


# ─── ジョブ作成 ─────────────────────────────────────────────────────────────

def test_job_作成(client: TestClient):
    with patch.object(run_sample_job, "kiq", new_callable=AsyncMock):
        res = client.post(
            "/api/jobs",
            json={"name": "sample", "params": {"seconds": 5}},
        )
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "sample"
    assert data["status"] == "pending"
    assert data["progress"] == 0
    assert "id" in data


def test_job_不明な種別は400(client: TestClient):
    res = client.post(
        "/api/jobs",
        json={"name": "unknown_task", "params": {}},
    )
    assert res.status_code == 400


# ─── ジョブ取得 ─────────────────────────────────────────────────────────────

def test_job_単一取得(client: TestClient):
    with patch.object(run_sample_job, "kiq", new_callable=AsyncMock):
        created = client.post(
            "/api/jobs",
            json={"name": "sample", "params": {"seconds": 5}},
        ).json()

    res = client.get(f"/api/jobs/{created['id']}")
    assert res.status_code == 200
    assert res.json()["id"] == created["id"]


def test_job_存在しないidは404(client: TestClient):
    res = client.get("/api/jobs/00000000-0000-0000-0000-000000000000")
    assert res.status_code == 404


# ─── ジョブキャンセル ────────────────────────────────────────────────────────

def test_job_キャンセル_pending状態(client: TestClient):
    with patch.object(run_sample_job, "kiq", new_callable=AsyncMock):
        created = client.post(
            "/api/jobs",
            json={"name": "sample", "params": {"seconds": 10}},
        ).json()

    res = client.delete(f"/api/jobs/{created['id']}")
    assert res.status_code == 204


def test_job_キャンセル_存在しないidは404(client: TestClient):
    res = client.delete("/api/jobs/00000000-0000-0000-0000-000000000000")
    assert res.status_code == 404


def test_job_キャンセル済みは再キャンセル不可(client: TestClient):
    with patch.object(run_sample_job, "kiq", new_callable=AsyncMock):
        created = client.post(
            "/api/jobs",
            json={"name": "sample", "params": {"seconds": 10}},
        ).json()

    client.delete(f"/api/jobs/{created['id']}")
    res = client.delete(f"/api/jobs/{created['id']}")
    assert res.status_code == 400  # キャンセル済みは 400 Bad Request


# ─── ユーザー分離（raw_client + 実JWTで確認） ───────────────────────────────

def test_job_ユーザーAのジョブをユーザーBは見えない(
    session: Session, raw_client: TestClient, test_user: User, second_user: User
):
    # サービス層でユーザーAのジョブを直接作成（Taskiqは不要）
    job_svc.create_job(
        session, str(uuid.uuid4()), JobCreate(name="sample", params={"seconds": 5}), test_user.id
    )

    # ユーザーBとして一覧取得 → 空のはず
    res = raw_client.get("/api/jobs", headers=make_auth_headers(second_user))
    assert res.status_code == 200
    assert res.json() == []


def test_job_ユーザーAのジョブをユーザーBは取得できない(
    session: Session, raw_client: TestClient, test_user: User, second_user: User
):
    job = job_svc.create_job(
        session, str(uuid.uuid4()), JobCreate(name="sample", params={"seconds": 5}), test_user.id
    )

    res = raw_client.get(f"/api/jobs/{job.id}", headers=make_auth_headers(second_user))
    assert res.status_code == 404


def test_job_ユーザーAのジョブをユーザーBはキャンセルできない(
    session: Session, raw_client: TestClient, test_user: User, second_user: User
):
    job = job_svc.create_job(
        session, str(uuid.uuid4()), JobCreate(name="sample", params={"seconds": 5}), test_user.id
    )

    res = raw_client.delete(f"/api/jobs/{job.id}", headers=make_auth_headers(second_user))
    assert res.status_code == 404
