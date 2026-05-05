from __future__ import annotations

import os
from datetime import datetime, timedelta, UTC
from typing import Optional

import jwt
from bcrypt import checkpw, hashpw, gensalt
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from app.models import models

load_dotenv()

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_HOURS", "24"))
JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "30"))


def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    salt = gensalt(rounds=12)
    return hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash using bcrypt."""
    return checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_tokens(user_id: int) -> dict[str, str | int]:
    """Create access and refresh tokens."""
    now = datetime.now(UTC)
    
    # Access token
    access_token_expires = now + timedelta(hours=JWT_ACCESS_TOKEN_EXPIRE_HOURS)
    access_token_payload = {
        "sub": str(user_id),
        "type": "access",
        "iat": now.timestamp(),
        "exp": access_token_expires.timestamp(),
    }
    access_token = jwt.encode(
        access_token_payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )
    
    # Refresh token
    refresh_token_expires = now + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token_payload = {
        "sub": str(user_id),
        "type": "refresh",
        "iat": now.timestamp(),
        "exp": refresh_token_expires.timestamp(),
    }
    refresh_token = jwt.encode(
        refresh_token_payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "access_token_expires": int(JWT_ACCESS_TOKEN_EXPIRE_HOURS * 3600),
    }


def decode_token(token: str) -> dict[str, any] | None:
    """Decode and validate JWT token."""
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_user_by_email(db: Session, email: str) -> models.User | None:
    """Get user by email."""
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_username(db: Session, username: str) -> models.User | None:
    """Get user by username."""
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_id(db: Session, user_id: int) -> models.User | None:
    """Get user by ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()


def create_user(
    db: Session,
    username: str,
    email: str,
    password: str,
) -> models.User:
    """Create new user with hashed password."""
    hashed_password = hash_password(password)
    user = models.User(
        username=username,
        email=email,
        password_hash=hashed_password,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def verify_credentials(db: Session, email: str, password: str) -> models.User | None:
    """Verify user credentials."""
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        return None
    return user
