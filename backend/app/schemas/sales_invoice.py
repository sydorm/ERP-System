from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal
from typing import List, Optional
from datetime import date
from uuid import UUID
from app.models.sales_invoice import SalesInvoiceStatus

class SalesInvoiceLineBase(BaseModel):
    """Base Sales Invoice Line schema"""
    product_id: UUID
    quantity: Decimal = Field(..., gt=0)
    price: Decimal = Field(..., ge=0)
    total: Decimal = Field(..., ge=0)

class SalesInvoiceLineCreate(SalesInvoiceLineBase):
    """Schema for creating a sales invoice line"""
    pass

class SalesInvoiceLineResponse(SalesInvoiceLineBase):
    """Schema for sales invoice line response"""
    id: UUID
    
    model_config = ConfigDict(from_attributes=True)

class SalesInvoiceBase(BaseModel):
    """Base Sales Invoice schema"""
    invoice_number: str = Field(..., min_length=1, max_length=50)
    invoice_date: date = Field(default_factory=date.today)
    
    counterparty_id: UUID
    warehouse_id: UUID
    order_id: Optional[UUID] = None
    
    currency: str = "UAH"
    total_amount: Decimal = Field(default=Decimal("0.00"), ge=0)

class SalesInvoiceCreate(SalesInvoiceBase):
    """Schema for creating a sales invoice"""
    lines: List[SalesInvoiceLineCreate]

class SalesInvoiceUpdate(BaseModel):
    """Schema for updating a sales invoice"""
    invoice_number: Optional[str] = None
    invoice_date: Optional[date] = None
    status: Optional[SalesInvoiceStatus] = None
    
    counterparty_id: Optional[UUID] = None
    warehouse_id: Optional[UUID] = None
    
    lines: Optional[List[SalesInvoiceLineCreate]] = None

class SalesInvoiceResponse(SalesInvoiceBase):
    """Schema for sales invoice response"""
    id: UUID
    status: SalesInvoiceStatus
    company_id: UUID
    created_by: Optional[UUID] = None
    
    lines: List[SalesInvoiceLineResponse]
    
    model_config = ConfigDict(from_attributes=True)
