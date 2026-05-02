from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from decimal import Decimal

class PurchaseOrderStatus(str):
    pass

class PurchaseOrderLineBase(BaseModel):
    product_id: UUID
    variant_id: Optional[UUID] = None
    quantity: Decimal = Field(..., ge=0)
    price: Decimal = Field(..., ge=0)
    total: Decimal = Field(..., ge=0)
    attribute_values: Optional[List[dict]] = None

class PurchaseOrderLineCreate(PurchaseOrderLineBase):
    pass

class PurchaseOrderLineResponse(PurchaseOrderLineBase):
    id: UUID
    order_id: UUID
    class Config:
        from_attributes = True

class PurchaseOrderBase(BaseModel):
    order_number: Optional[str] = "Авто"
    order_date: datetime
    expected_date: Optional[datetime] = None
    supplier_id: UUID
    warehouse_id: UUID
    currency: str = "UAH"
    total_amount: Decimal = Field(0, ge=0)
    notes: Optional[str] = None
    status: Optional[str] = "draft"

class PurchaseOrderCreate(PurchaseOrderBase):
    lines: List[PurchaseOrderLineCreate]

class PurchaseOrderUpdate(BaseModel):
    order_date: Optional[datetime] = None
    expected_date: Optional[datetime] = None
    supplier_id: Optional[UUID] = None
    warehouse_id: Optional[UUID] = None
    status: Optional[str] = None
    total_amount: Optional[Decimal] = None
    notes: Optional[str] = None
    lines: Optional[List[PurchaseOrderLineCreate]] = None

class PurchaseOrderResponse(PurchaseOrderBase):
    id: UUID
    company_id: UUID
    created_by: UUID
    lines: List[PurchaseOrderLineResponse]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PurchaseTemplateLineBase(BaseModel):
    product_id: UUID
    variant_id: Optional[UUID] = None
    quantity: Decimal = Field(..., ge=0)
    attribute_values: Optional[List[dict]] = None

class PurchaseTemplateLineCreate(PurchaseTemplateLineBase):
    pass

class PurchaseTemplateLineResponse(PurchaseTemplateLineBase):
    id: UUID
    template_id: UUID
    class Config:
        from_attributes = True

class PurchaseTemplateBase(BaseModel):
    name: str
    supplier_id: Optional[UUID] = None
    warehouse_id: Optional[UUID] = None
    notes: Optional[str] = None

class PurchaseTemplateCreate(PurchaseTemplateBase):
    lines: List[PurchaseTemplateLineCreate]

class PurchaseTemplateResponse(PurchaseTemplateBase):
    id: UUID
    company_id: UUID
    created_by: UUID
    lines: List[PurchaseTemplateLineResponse]
    class Config:
        from_attributes = True
