from fastapi import Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from app.database import get_session
from app.models.user import User
from app.services.auth import decode_token

bearer_scheme = HTTPBearer(auto_error=False)


def _get_user_from_token(token: str, session: Session) -> User:
    user_id = decode_token(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="認証が必要です")
    user = session.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="無効なユーザーです")
    return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: Session = Depends(get_session),
) -> User:
    if not credentials:
        raise HTTPException(status_code=401, detail="認証が必要です")
    return _get_user_from_token(credentials.credentials, session)


def get_current_user_from_query(
    token: str | None = Query(None),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: Session = Depends(get_session),
) -> User:
    """SSEエンドポイント用: Bearer headerまたはクエリパラメータ ?token= を受け付ける。"""
    raw = token or (credentials.credentials if credentials else None)
    if not raw:
        raise HTTPException(status_code=401, detail="認証が必要です")
    return _get_user_from_token(raw, session)
