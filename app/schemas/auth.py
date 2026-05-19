"""Auth request and response schemas (Pydantic)."""
from pydantic import BaseModel


class RegisterRequest(BaseModel):
    """Request body for POST /auth/register."""
    username: str
    password: str


class LoginRequest(BaseModel):
    """Request body for POST /auth/login."""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Response for successful auth."""
    access_token: str
    token_type: str = "bearer"
