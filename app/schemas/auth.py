"""Auth request and response schemas (Pydantic)."""
from pydantic import BaseModel, field_validator


class RegisterRequest(BaseModel):
    """Request body for POST /auth/register."""
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def username_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("username must be a non-empty string")
        return v

    @field_validator("password")
    @classmethod
    def password_not_empty(cls, v: str) -> str:
        if not v:
            raise ValueError("password must not be empty")
        return v


class LoginRequest(BaseModel):
    """Request body for POST /auth/login."""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Response for successful auth."""
    access_token: str
    token_type: str = "bearer"
