"""
Company schemas
"""
from pydantic import BaseModel, Field, HttpUrl, EmailStr
from typing import Optional, List
from uuid import UUID
from enum import Enum
from .bank_account import BankAccountResponse, BankAccountCreate

class CompanyType(str, Enum):
    FOP = "FOP"
    TOV = "TOV"

class TaxGroup(str, Enum):
    GROUP_1 = "GROUP_1"
    GROUP_2 = "GROUP_2"
    GROUP_3 = "GROUP_3"
    GENERAL = "GENERAL"

class CompanyBase(BaseModel):
    # Basic Info
    name: str = Field(..., min_length=1, max_length=255)
    full_name_uk: Optional[str] = None
    short_name_uk: Optional[str] = None
    full_name_en: Optional[str] = None
    website: Optional[str] = None
    
    # Registration
    edrpou: Optional[str] = Field(None, max_length=20)
    ipn: Optional[str] = Field(None, max_length=20)
    kved: Optional[str] = Field(None, max_length=10)
    
    # Signatories
    director_name: Optional[str] = None
    director_position: Optional[str] = None
    accountant_name: Optional[str] = None
    
    # Addresses
    legal_address: Optional[str] = None
    physical_address: Optional[str] = None
    
    # Contacts
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    
    # Tax
    company_type: CompanyType = CompanyType.FOP
    tax_group: Optional[TaxGroup] = None
    vat_payer: bool = False
    vat_number: Optional[str] = None

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(CompanyBase):
    pass

class CompanyResponse(CompanyBase):
    id: UUID
    is_active: bool
    bank_accounts: List[BankAccountResponse] = []

    class Config:
        from_attributes = True

# Schemas for Registration Flow
class CompanyRegInfo(BaseModel):
    name: str
    legalForm: CompanyType
    taxId: str

class AdminRegInfo(BaseModel):
    firstName: str
    lastName: str
    email: str
    password: str

class SettingsRegInfo(BaseModel):
    warehouseName: str
    currency: str
    timezone: str

class CompanyRegistrationRequest(BaseModel):
    company: CompanyRegInfo
    admin: AdminRegInfo
    settings: SettingsRegInfo
