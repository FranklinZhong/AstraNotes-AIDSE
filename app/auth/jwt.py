"""JWT token creation and verification.

Usage:
    token = create_token(user_id="alice")
    user_id = verify_token(token)  # returns "alice"
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt

from app.config import settings  # single source of config

ALGORITHM: str = "HS256"


def create_token(user_id: str) -> str:
    """Return a signed JWT containing the given user_id."""
    payload = {
        "sub": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=settings.jwt_expire_hours),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)


def verify_token(token: str) -> str:
    """Decode and verify a JWT. Returns user_id (sub claim).

    Raises jwt.InvalidTokenError on failure.
    """
    payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
    return str(payload["sub"])
