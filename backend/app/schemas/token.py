"""
Token schemas for authentication
"""
from pydantic import BaseModel
from uuid import UUID


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Data encoded in JWT token"""
    user_id: UUID
    email: str
    company_id: UUID
