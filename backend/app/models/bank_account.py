"""
Bank Account model
"""
from sqlalchemy import Column, String, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from .base import BaseModel

class Currency(str, enum.Enum):
    UAH = "UAH"
    USD = "USD"
    EUR = "EUR"

class BankAccount(BaseModel):
    """
    Bank Account model
    Represents a bank account (IBAN) for a company
    """
    __tablename__ = "bank_accounts"

    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    
    bank_name = Column(String(255), nullable=True) # Bank Name / Назва банку
    mfo = Column(String(10), nullable=True)        # MFO / МФО (Code of bank)
    iban = Column(String(34), nullable=False)      # IBAN / Рахунок IBAN (Unique per currency theoretically, but one account has one IBAN)
    currency = Column(Enum(Currency), default=Currency.UAH, nullable=False) # Currency / Валюта
    
    is_primary = Column(Boolean, default=False)    # Primary account for this currency / Основний
    description = Column(String(255), nullable=True) # Description / Примітка (e.g. "Card account")

    # Relationships
    company = relationship("Company", back_populates="bank_accounts")

    def __repr__(self):
        return f"<BankAccount {self.iban} ({self.currency})>"
