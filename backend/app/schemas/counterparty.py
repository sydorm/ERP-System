from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID

class CounterpartyBase(BaseModel):
    """Base Counterparty schema"""
    name: str = Field(..., min_length=1, max_length=255)
    legal_name: Optional[str] = Field(None, max_length=500)
    tax_id: Optional[str] = Field(None, max_length=50)
    
    is_customer: bool = True
    is_supplier: bool = False
    
    phone: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = None
    address: Optional[str] = Field(None, max_length=500)
    default_contract: Optional[str] = Field(None, max_length=255)
    
    # Procurement settings
    delivery_days: Optional[int] = Field(0, ge=0)
    payment_terms: Optional[str] = Field(None, max_length=255)
    
    is_active: bool = True

class CounterpartyCreate(CounterpartyBase):
    """Schema for creating a counterparty"""
    pass

class CounterpartyUpdate(BaseModel):
    """Schema for updating a counterparty"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    legal_name: Optional[str] = Field(None, max_length=500)
    tax_id: Optional[str] = Field(None, max_length=50)
    
    is_customer: Optional[bool] = None
    is_supplier: Optional[bool] = None
    
    phone: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = None
    address: Optional[str] = Field(None, max_length=500)
    default_contract: Optional[str] = Field(None, max_length=255)
    
    delivery_days: Optional[int] = None
    payment_terms: Optional[str] = None
    
    is_active: Optional[bool] = None

class CounterpartyResponse(CounterpartyBase):
    """Schema for counterparty response"""
    id: UUID
    company_id: UUID

    class Config:
        from_attributes = True
