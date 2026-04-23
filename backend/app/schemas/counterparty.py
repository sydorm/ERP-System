from typing import Optional, List
from pydantic import BaseModel, Field
from uuid import UUID
from decimal import Decimal
from datetime import datetime

class BankAccountBase(BaseModel):
    bank_name: Optional[str] = None
    iban: str
    currency: str = "UAH"
    purpose: Optional[str] = None
    is_active: bool = True

class BankAccountCreate(BankAccountBase):
    pass

class BankAccountResponse(BankAccountBase):
    id: UUID
    counterparty_id: UUID
    class Config:
        from_attributes = True

class ContactBase(BaseModel):
    name: str
    position: Optional[str] = None
    phone: Optional[str] = None
    telegram: Optional[str] = None
    email: Optional[str] = None
    is_primary: bool = False

class ContactCreate(ContactBase):
    pass

class ContactResponse(ContactBase):
    id: UUID
    counterparty_id: UUID
    class Config:
        from_attributes = True

class CounterpartyMaterialBase(BaseModel):
    product_id: UUID
    price: Decimal
    currency: str = "UAH"

class CounterpartyMaterialCreate(CounterpartyMaterialBase):
    pass

class CounterpartyMaterialResponse(CounterpartyMaterialBase):
    id: UUID
    counterparty_id: UUID
    product_name: Optional[str] = None
    class Config:
        from_attributes = True

class CounterpartyDocumentResponse(BaseModel):
    id: UUID
    counterparty_id: UUID
    name: str
    file_url: str
    created_at: datetime
    class Config:
        from_attributes = True

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
    payment_terms_id: Optional[UUID] = None
    payment_terms: Optional[str] = Field(None, max_length=255)
    
    # New fields
    acquisition_channel_id: Optional[UUID] = None
    city: Optional[str] = None
    np_department: Optional[str] = None
    discount_percent: Optional[int] = 0
    notes: Optional[str] = None
    tags: Optional[list] = None
    min_order_amount: Optional[Decimal] = Decimal("0.00")
    contact_person: Optional[str] = None
    supplied_materials: Optional[str] = None
    
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
    payment_terms_id: Optional[UUID] = None
    payment_terms: Optional[str] = None
    
    acquisition_channel_id: Optional[UUID] = None
    city: Optional[str] = None
    np_department: Optional[str] = None
    discount_percent: Optional[int] = None
    notes: Optional[str] = None
    tags: Optional[list] = None
    min_order_amount: Optional[Decimal] = None
    contact_person: Optional[str] = None
    supplied_materials: Optional[str] = None
    
    is_active: Optional[bool] = None

class CounterpartyResponse(CounterpartyBase):
    """Schema for counterparty response"""
    id: UUID
    company_id: UUID
    
    bank_accounts: List[BankAccountResponse] = []
    contacts: List[ContactResponse] = []
    materials: List[CounterpartyMaterialResponse] = []
    documents: List[CounterpartyDocumentResponse] = []

    class Config:
        from_attributes = True
