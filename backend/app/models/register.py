from sqlalchemy import Column, String, Numeric, ForeignKey, DateTime, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import enum
from .base import BaseModel

class RegisterType(enum.Enum):
    STOCK = "stock"
    FINANCE = "finance"
    AR_AP = "ar_ap" # Accounts Receivable / Accounts Payable

class AccumulationRegister(BaseModel):
    """
    Central register for all value movements.
    Stores 'increments' (+) and 'decrements' (-) to track balances.
    """
    __tablename__ = "accumulation_registers"

    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    
    # Type of movement
    register_type = Column(Enum(RegisterType), nullable=False, index=True)
    
    # Dimensions (What we are tracking)
    # Generic dimensions to support stock (product/warehouse), money (account), or debt (counterparty)
    # Using specific columns for core dimensions for performance
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=True, index=True)
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=True, index=True)
    counterparty_id = Column(UUID(as_uuid=True), ForeignKey("counterparties.id"), nullable=True, index=True)
    bank_account_id = Column(UUID(as_uuid=True), ForeignKey("bank_accounts.id"), nullable=True, index=True)
    
    # Resources (How much)
    quantity = Column(Numeric(15, 4), default=0) # For stock
    amount = Column(Numeric(15, 2), default=0)   # For money/value
    currency = Column(String(3), default="UAH")
    
    # Reference to the document that created this record
    document_type = Column(String(50), nullable=False, index=True) # e.g., "Order", "Receipt", "Invoice"
    document_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Metadata
    notes = Column(String(500), nullable=True)
    extra_data = Column(JSON, nullable=True) # For any additional dimensions
