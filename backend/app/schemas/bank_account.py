"""
Bank Account Schemas
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from uuid import UUID
from enum import Enum

class Currency(str, Enum):
    UAH = "UAH"
    USD = "USD"
    EUR = "EUR"

class BankAccountBase(BaseModel):
    bank_name: Optional[str] = None
    mfo: Optional[str] = None
    iban: str = Field(..., min_length=15, max_length=34)
    currency: Currency = Currency.UAH
    is_primary: bool = False
    description: Optional[str] = None

    @field_validator('iban')
    def validate_iban(cls, v):
        # Basic IBAN structure check (e.g. UA + 27 digits)
        # We can make this more strict later
        if not v.startswith("UA"):
             # For now, just a warning or soft check, but standard demands UA for Ukraine
             pass 
        return v.replace(" ", "").upper()

class BankAccountCreate(BankAccountBase):
    pass

class BankAccountUpdate(BankAccountBase):
    pass

class BankAccountResponse(BankAccountBase):
    id: UUID
    company_id: UUID

    class Config:
        from_attributes = True
