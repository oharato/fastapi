import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_session
from app.core.deps import get_current_user
from app.models.user import User
from app.services.auth import hash_password, create_access_token


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session) -> User:
    user = User(email="test@example.com", hashed_password=hash_password("test"))
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="second_user")
def second_user_fixture(session: Session) -> User:
    user = User(email="second@example.com", hashed_password=hash_password("test2"))
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="client")
def client_fixture(session: Session, test_user: User):
    """認証をバイパスしたクライアント（TODOとジョブのロジックテスト用）"""
    def get_session_override():
        yield session

    def get_current_user_override():
        return test_user

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_current_user] = get_current_user_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="second_client")
def second_client_fixture(session: Session, second_user: User):
    """2人目のユーザーとしてアクセスするクライアント（ユーザー分離テスト用）"""
    def get_session_override():
        yield session

    def get_current_user_override():
        return second_user

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_current_user] = get_current_user_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="raw_client")
def raw_client_fixture(session: Session):
    """認証バイパスなしのクライアント（認証エンドポイントのテスト用）"""
    def get_session_override():
        yield session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def make_auth_headers(user: User) -> dict:
    """テスト用JWTトークンを生成してAuthorizationヘッダーを返す"""
    token = create_access_token(user.id)
    return {"Authorization": f"Bearer {token}"}
