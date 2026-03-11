from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.core.deps import get_current_user
from app.database import get_session
from app.models.user import User
from app.schemas.auth import LoginRequest, Token, UserRead
from app.services.auth import authenticate_user, create_access_token

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(data: LoginRequest, session: Session = Depends(get_session)):
    user = authenticate_user(session, data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="メールアドレスまたはパスワードが正しくありません")
    return Token(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)):
    return current_user
