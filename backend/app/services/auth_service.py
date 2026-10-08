from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.session import AuthSession
from app.models.user import User
from app.schemas.auth import UserCreate, UserLogin
from app.utils.security import create_access_token, hash_password, verify_password


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email.lower()))


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def register_user(db: Session, payload: UserCreate) -> User:
    existing = get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        first_name=payload.first_name.strip(),
        last_name=payload.last_name.strip(),
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, payload: UserLogin) -> User:
    user = get_user_by_email(db, payload.email)
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if not user.active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled")
    return user


def issue_token_for_user(db: Session, user: User) -> str:
    token, jti, expires_at = create_access_token(subject=str(user.user_id))
    session = AuthSession(user_id=user.user_id, token_jti=jti, expires_at=expires_at)
    db.add(session)
    db.commit()
    return token


def is_session_valid(db: Session, *, user_id: int, jti: str) -> bool:
    session = db.scalar(
        select(AuthSession).where(AuthSession.user_id == user_id, AuthSession.token_jti == jti)
    )
    if session is None:
        return False
    expires_at = session.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    return expires_at > datetime.now(timezone.utc)
