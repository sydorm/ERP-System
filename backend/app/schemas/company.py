"""
Company schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from enum import Enum

class CompanyType(str, Enum):
    FOP = "FOP"
    TOV = "TOV"
    PP = "PP"
    AT = "AT"

class CompanyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    legal_name: Optional[str] = None
    tax_id: str = Field(..., min_length=8, max_length=12)
    company_type: CompanyType

class CompanyCreate(CompanyBase):
    pass

class CompanyResponse(CompanyBase):
    id: UUID
    is_active: bool

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
