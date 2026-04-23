from typing import Optional, List
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class BrigadeMemberBase(BaseModel):
    employee_id: UUID
    role_type: str = "main" # main, reserve
    is_active: bool = True

class BrigadeMemberCreate(BrigadeMemberBase):
    pass

class BrigadeMemberUpdate(BrigadeMemberBase):
    employee_id: Optional[UUID] = None
    role_type: Optional[str] = None
    is_active: Optional[bool] = None

class BrigadeMember(BrigadeMemberBase):
    id: UUID
    brigade_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class BrigadeBase(BaseModel):
    name: str
    stage_id: Optional[UUID] = None
    is_active: bool = True

class BrigadeCreate(BrigadeBase):
    members: Optional[List[BrigadeMemberCreate]] = None

class BrigadeUpdate(BrigadeBase):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    members: Optional[List[BrigadeMemberCreate]] = None

class Brigade(BrigadeBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    members: List[BrigadeMember] = []

    class Config:
        from_attributes = True
