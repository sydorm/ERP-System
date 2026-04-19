"""
Financial Transaction model
Tracks all money movements on bank accounts
"""
from sqlalchemy import Column, String, Numeric, ForeignKey, DateTime, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from .base import BaseModel

class TransactionType(str, enum.Enum):
    IN = "IN"   # Income / Прихід
    OUT = "OUT" # Expense / Вихід

class FinancialTransaction(BaseModel):
    """
    Financial Transaction
    A single money movement on a bank account
    """
    __tablename__ = "financial_transactions"

    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    bank_account_id = Column(UUID(as_uuid=True), ForeignKey("bank_accounts.id", ondelete="RESTRICT"), nullable=False, index=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="SET NULL"), nullable=True, index=True)
    
    transaction_type = Column(Enum(TransactionType), nullable=False, default=TransactionType.IN)
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="UAH")
    
    transaction_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    description = Column(String(500), nullable=True)
    
    # Metadata for grouping
    category = Column(String(50), nullable=True, index=True) # e.g. "SALES", "TAX", "RENT"
    
    # Relationships
    company = relationship("Company", backref="financial_transactions")
    bank_account = relationship("BankAccount", backref="financial_transactions")
    order = relationship("Order", backref="financial_transactions")

    def __repr__(self):
        return f"<FinancialTransaction {self.transaction_type} {self.amount} {self.currency}>"
