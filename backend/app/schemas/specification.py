from typing import Optional, List
from pydantic import BaseModel, Field
from decimal import Decimal
from uuid import UUID
from datetime import datetime

class SpecificationItemBase(BaseModel):
    component_id: UUID
    quantity: Decimal = Field(..., ge=0.0001)
    unit_of_measure: Optional[str] = None
    notes: Optional[str] = None

class SpecificationItemCreate(SpecificationItemBase):
    pass

class ComponentBasicInfo(BaseModel):
    id: UUID
    name: str
    sku: str
    
    class Config:
        from_attributes = True

class SpecificationItemResponse(SpecificationItemBase):
    id: UUID
    component: Optional[ComponentBasicInfo] = None
    
    class Config:
        from_attributes = True

class ProductSpecificationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    is_active: bool = True
    is_default: bool = False
    notes: Optional[str] = None

class ProductSpecificationCreate(ProductSpecificationBase):
    items: List[SpecificationItemCreate] = []

class ProductSpecificationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None
    notes: Optional[str] = None
    items: Optional[List[SpecificationItemCreate]] = None

class ProductSpecificationResponse(ProductSpecificationBase):
    id: UUID
    product_id: UUID
    items: List[SpecificationItemResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
