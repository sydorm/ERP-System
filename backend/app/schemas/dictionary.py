from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID

class DictionaryItemBase(BaseModel):
    category: str = Field(..., min_length=1, max_length=50)
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    color: Optional[str] = None
    icon: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True

class DictionaryItemCreate(DictionaryItemBase):
    pass

class DictionaryItemUpdate(BaseModel):
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    color: Optional[str] = None
    icon: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None

class DictionaryItemResponse(DictionaryItemBase):
    id: UUID
    company_id: UUID
    is_fixed: bool

    class Config:
        from_attributes = True
