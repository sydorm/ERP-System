from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

class PrintTemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    document_type: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    html_template: str
    css_template: Optional[str] = None
    is_default: bool = False
    is_active: bool = True

class PrintTemplateCreate(PrintTemplateBase):
    pass

class PrintTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    document_type: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None
    html_template: Optional[str] = None
    css_template: Optional[str] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None

class PrintTemplateResponse(PrintTemplateBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
