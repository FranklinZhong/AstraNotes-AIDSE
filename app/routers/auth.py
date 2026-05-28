"""Auth router — register/login with SQLite persistence and bcrypt hashing."""
from __future__ import annotations

from sqlalchemy import Column, MetaData, Table, Text, create_engine, insert, select
from sqlalchemy.pool import StaticPool
from passlib.context import CryptContext
from fastapi import APIRouter, HTTPException, status

from app.auth.jwt import create_token
from app.config import settings
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

_meta = MetaData()
_users_table = Table(
    "users", _meta,
    Column("username", Text, primary_key=True),
    Column("hashed_password", Text, nullable=False),
)

# Lazy engine — created on first request (not at import time)
_engine = None


def _get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(
            settings.database_url,
            connect_args={"check_same_thread": False},
        )
        _meta.create_all(_engine)
    return _engine


def verify_user_password(username: str, password: str) -> bool:
    """Return True if username exists and password matches stored hash."""
    eng = _get_engine()
    with eng.connect() as conn:
        row = conn.execute(
            select(_users_table).where(_users_table.c.username == username)
        ).first()
    if not row:
        return False
    return pwd_context.verify(password, row._mapping["hashed_password"])


def _reset_users_for_test(url: str = "sqlite:///:memory:") -> None:
    """Test helper: replace engine with a fresh isolated in-memory one.

    Uses StaticPool so all connections share the same in-memory database,
    preventing 'no such table' errors between create_all and query calls.
    """
    global _engine
    _engine = create_engine(
        url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    _meta.create_all(_engine)


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(req: RegisterRequest):
    eng = _get_engine()
    with eng.connect() as conn:
        existing = conn.execute(
            select(_users_table).where(_users_table.c.username == req.username)
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists",
            )
        conn.execute(
            insert(_users_table).values(
                username=req.username,
                hashed_password=pwd_context.hash(req.password),
            )
        )
        conn.commit()
    return TokenResponse(access_token=create_token(user_id=req.username))


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest):
    eng = _get_engine()
    with eng.connect() as conn:
        row = conn.execute(
            select(_users_table).where(_users_table.c.username == req.username)
        ).first()
    if not row or not pwd_context.verify(req.password, row._mapping["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    return TokenResponse(access_token=create_token(user_id=req.username))
