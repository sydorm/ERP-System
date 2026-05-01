from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal
from typing import Any, Dict, List, Optional
from datetime import date, datetime
from uuid import UUID
from app.schemas.variant import VariantValueCreate


class OrderLineBase(BaseModel):
    product_id: UUID
    variant_id: Optional[UUID] = None
    quantity: Decimal = Field(..., gt=0)
    price: Decimal = Field(..., ge=0)
    total: Decimal = Field(..., ge=0)
    variant_values: Optional[List[VariantValueCreate]] = None
    attribute_values: Optional[List[dict]] = None
    characteristic_width: Optional[Decimal] = None
    characteristic_height: Optional[Decimal] = None
    specification_id: Optional[UUID] = None


class OrderLineCreate(OrderLineBase):
    pass


class OrderLineResponse(OrderLineBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)


class OrderBase(BaseModel):
    order_number: str = Field(..., min_length=1, max_length=50)
    order_date: date = Field(default_factory=date.today)
    shipping_date: Optional[date] = None

    counterparty_id: UUID
    warehouse_id: UUID

    contract: Optional[str] = Field(None, max_length=255)
    comment: Optional[str] = None

    total_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    discount_percent: Optional[Decimal] = Field(default=Decimal("0.00"), ge=0, le=100)

    # CRM fields
    crm_stage: str = Field(default="new", max_length=50)
    channel: Optional[str] = Field(None, max_length=50)
    lead_source_id: Optional[UUID] = None
    city: Optional[str] = Field(None, max_length=255)
    delivery_type: Optional[str] = Field(None, max_length=50)
    delivery_method_id: Optional[UUID] = None
    attributes_values: Optional[Dict[str, Any]] = None

    paid_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    payment_status: str = Field(default="unpaid", max_length=50)
    payment_status_id: Optional[UUID] = None
    prepayment_percent: Optional[Decimal] = Field(None, ge=0, le=100)
    prepayment_amount: Optional[Decimal] = Field(None, ge=0)

    deadline_date: Optional[date] = None
    next_contact_date: Optional[date] = None
    next_contact_at: Optional[datetime] = None
    next_contact_channel: Optional[str] = Field(None, max_length=50)
    next_contact_comment: Optional[str] = None

    priority: str = Field(default="normal", max_length=20)
    priority_id: Optional[UUID] = None
    manager_id: Optional[UUID] = None

    internal_notes: Optional[str] = None
    reference_photo: Optional[str] = Field(None, max_length=500)
    bank_account_id: Optional[UUID] = None

    
    # Additional IDs
    cancel_reason_id: Optional[UUID] = None
    client_type_id: Optional[UUID] = None



class OrderCreate(OrderBase):
    lines: List[OrderLineCreate]


class OrderUpdate(BaseModel):
    order_number: Optional[str] = Field(None, min_length=1, max_length=50)
    order_date: Optional[date] = None
    shipping_date: Optional[date] = None
    status: Optional[str] = None
    counterparty_id: Optional[UUID] = None
    warehouse_id: Optional[UUID] = None
    contract: Optional[str] = Field(None, max_length=255)
    comment: Optional[str] = None
    discount_percent: Optional[Decimal] = Field(None, ge=0, le=100)
    total_amount: Optional[Decimal] = Field(None, ge=0)

    # CRM fields
    crm_stage: Optional[str] = Field(None, max_length=50)
    channel: Optional[str] = Field(None, max_length=50)
    lead_source_id: Optional[UUID] = None
    city: Optional[str] = Field(None, max_length=255)
    delivery_type: Optional[str] = Field(None, max_length=50)
    delivery_method_id: Optional[UUID] = None
    attributes_values: Optional[Dict[str, Any]] = None
    paid_amount: Optional[Decimal] = Field(None, ge=0)
    payment_status: Optional[str] = Field(None, max_length=50)
    payment_status_id: Optional[UUID] = None
    prepayment_percent: Optional[Decimal] = Field(None, ge=0, le=100)
    prepayment_amount: Optional[Decimal] = Field(None, ge=0)
    deadline_date: Optional[date] = None
    next_contact_date: Optional[date] = None
    next_contact_at: Optional[datetime] = None
    next_contact_channel: Optional[str] = Field(None, max_length=50)
    next_contact_comment: Optional[str] = None
    priority: Optional[str] = Field(None, max_length=20)
    priority_id: Optional[UUID] = None
    manager_id: Optional[UUID] = None
    internal_notes: Optional[str] = None
    reference_photo: Optional[str] = Field(None, max_length=500)
    bank_account_id: Optional[UUID] = None

    
    cancel_reason_id: Optional[UUID] = None
    client_type_id: Optional[UUID] = None


    lines: Optional[List[OrderLineCreate]] = None


class OrderResponse(OrderBase):
    id: UUID
    status: str
    company_id: UUID
    created_by: Optional[UUID] = None
    created_by_name: Optional[str] = None
    manager_name: Optional[str] = None
    contact_attempts: int = 0
    lines: List[OrderLineResponse]
    product_summary: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class MaterialCheckItem(BaseModel):
    component_id: UUID
    component_name: str
    component_sku: str
    unit_of_measure: str
    required_qty: Decimal
    available_qty: Decimal
    status: str  # ok / low / missing


class MaterialCheckResponse(BaseModel):
    order_id: UUID
    product_id: Optional[UUID]
    has_issues: bool
    items: List[MaterialCheckItem]
