from __future__ import annotations

import hashlib
import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from db import SessionLocal
from models import User
from schemas import AuthResponse, MessageResponse, UserLogin, UserRegister

router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_db():
    with SessionLocal() as session:
        yield session


def _normalize_username(username: str) -> str:
    return username.strip()


def _hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100_000,
    ).hex()
    return f"{salt}${password_hash}"


def _verify_password(password: str, stored_password_hash: str) -> bool:
    salt, expected_hash = stored_password_hash.split("$", 1)
    actual_hash = _hash_password(password, salt).split("$", 1)[1]
    return secrets.compare_digest(actual_hash, expected_hash)


def get_current_user(
    x_user_id: Annotated[int | None, Header(alias="X-User-Id")] = None,
    session: Session = Depends(get_auth_db),
) -> User:
    if x_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    user = session.get(User, x_user_id)
    if user is None or not user.is_logged_in:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    return user


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    payload: UserRegister,
    session: Session = Depends(get_auth_db),
) -> dict[str, str | int]:
    username = _normalize_username(payload.username)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Username cannot be empty",
        )

    existing_user = session.scalar(select(User).where(User.username == username))
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this username already exists",
        )

    user = User(
        username=username,
        password_hash=_hash_password(payload.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"user_id": user.id, "message": "User registered successfully"}


@router.post("/login", response_model=AuthResponse)
def login_user(
    payload: UserLogin,
    session: Session = Depends(get_auth_db),
) -> dict[str, str | int]:
    username = _normalize_username(payload.username)
    user = session.scalar(select(User).where(User.username == username))

    if user is None or not _verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    user.is_logged_in = True
    session.commit()
    return {"user_id": user.id, "message": "User logged in successfully"}


@router.post("/logout", response_model=MessageResponse)
def logout_user(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_auth_db),
) -> dict[str, str]:
    user = session.get(User, current_user.id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    user.is_logged_in = False
    session.commit()
    return {"message": "User logged out successfully"}
