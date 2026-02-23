from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal
from typing import List, Optional
from datetime import date
from uuid import UUID
# from app.models.order import OrderStatus

class OrderLineBase(BaseModel):
    """Base Order Line schema"""
    product_id: UUID
    variant_id: Optional[UUID] = None
    quantity: Decimal = Field(..., gt=0)
    price: Decimal = Field(..., ge=0)
    total: Decimal = Field(..., ge=0)

class OrderLineCreate(OrderLineBase):
    """Schema for creating an order line"""
    pass

class OrderLineResponse(OrderLineBase):
    """Schema for order line response"""
    id: UUID
    
    model_config = ConfigDict(from_attributes=True)

class OrderBase(BaseModel):
    """Base Order schema"""
    order_number: str = Field(..., min_length=1, max_length=50)
    order_date: date = Field(default_factory=date.today)
    shipping_date: Optional[date] = None
    
    counterparty_id: UUID
    warehouse_id: UUID
    
    contract: Optional[str] = Field(None, max_length=255)
    comment: Optional[str] = None
    
    total_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    discount_percent: Optional[Decimal] = Field(default=Decimal("0.00"), ge=0, le=100)

class OrderCreate(OrderBase):
    """Schema for creating an order"""
    lines: List[OrderLineCreate]

class OrderUpdate(BaseModel):
    """Schema for updating an order"""
    order_number: Optional[str] = Field(None, min_length=1, max_length=50)
    order_date: Optional[date] = None
    shipping_date: Optional[date] = None
    status: Optional[str] = None
    
    counterparty_id: Optional[UUID] = None
    warehouse_id: Optional[UUID] = None
    
    contract: Optional[str] = Field(None, max_length=255)
    comment: Optional[str] = None
    discount_percent: Optional[Decimal] = Field(None, ge=0, le=100)
    
    lines: Optional[List[OrderLineCreate]] = None

class OrderResponse(OrderBase):
    """Schema for order response"""
    id: UUID
    status: str
    company_id: UUID
    created_by: Optional[UUID] = None
    
    lines: List[OrderLineResponse]
    
    model_config = ConfigDict(from_attributes=True)
