from sqlalchemy import Column, String, Date, ForeignKey, Numeric, Enum, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from decimal import Decimal
from datetime import date
import enum
from .base import BaseModel

class PurchaseReceiptStatus(str, enum.Enum):
    DRAFT = "draft"
    POSTED = "posted" # Standard ERP term / "Проведено"
    CANCELLED = "cancelled"

class PurchaseReceipt(BaseModel):
    """
    Purchase Receipt model (Прибуткова накладна)
    Represents the actual receipt of goods from a supplier.
    """
    __tablename__ = "purchase_receipts"
    
    receipt_number = Column(String(50), nullable=False, unique=True, index=True)
    receipt_date = Column(Date, nullable=False, default=date.today)
    
    status = Column(Enum(PurchaseReceiptStatus), nullable=False, default=PurchaseReceiptStatus.DRAFT)
    
    total_amount = Column(Numeric(15, 2), nullable=False, default=Decimal("0.00"))
    currency = Column(String(3), default="UAH")
    
    # Foreign Keys
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("counterparties.id", ondelete="RESTRICT"), nullable=False)
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id", ondelete="RESTRICT"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Relationships
    company = relationship("Company")
    supplier = relationship("Counterparty")
    warehouse = relationship("Warehouse")
    created_by_user = relationship("User")
    lines = relationship("PurchaseReceiptLine", back_populates="receipt", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<PurchaseReceipt {self.receipt_number} - {self.status}>"

class PurchaseReceiptLine(BaseModel):
    """
    Purchase Receipt Line model
    """
    __tablename__ = "purchase_receipt_lines"
    
    quantity = Column(Numeric(15, 3), nullable=False)
    price = Column(Numeric(15, 2), nullable=False)
    total = Column(Numeric(15, 2), nullable=False)
    
    # Foreign Keys
    receipt_id = Column(UUID(as_uuid=True), ForeignKey("purchase_receipts.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    
    # Relationships
    receipt = relationship("PurchaseReceipt", back_populates="lines")
    product = relationship("Product")
    
    def __repr__(self):
        return f"<PurchaseReceiptLine qty={self.quantity} price={self.price}>"
