from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID

class WarehouseBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    address: Optional[str] = None
    is_default: bool = False
    is_active: bool = True

class WarehouseCreate(WarehouseBase):
    pass

class WarehouseUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    address: Optional[str] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None

class WarehouseResponse(WarehouseBase):
    id: UUID
    company_id: UUID

    class Config:
        from_attributes = True
