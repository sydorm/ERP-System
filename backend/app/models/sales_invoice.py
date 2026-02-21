from sqlalchemy import Column, String, Date, ForeignKey, Numeric, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from decimal import Decimal
from datetime import date
import enum
from .base import BaseModel

class SalesInvoiceStatus(str, enum.Enum):
    DRAFT = "draft"
    POSTED = "posted"
    CANCELLED = "cancelled"

class SalesInvoice(BaseModel):
    """
    Sales Invoice model (Видаткова накладна)
    Represents the actual sale and delivery of goods.
    """
    __tablename__ = "sales_invoices"
    
    invoice_number = Column(String(50), nullable=False, unique=True, index=True)
    invoice_date = Column(Date, nullable=False, default=date.today)
    
    status = Column(Enum(SalesInvoiceStatus), nullable=False, default=SalesInvoiceStatus.DRAFT)
    
    total_amount = Column(Numeric(15, 2), nullable=False, default=Decimal("0.00"))
    currency = Column(String(3), default="UAH")
    
    # Foreign Keys
    counterparty_id = Column(UUID(as_uuid=True), ForeignKey("counterparties.id", ondelete="RESTRICT"), nullable=False)
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id", ondelete="RESTRICT"), nullable=False)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="SET NULL"), nullable=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Relationships
    company = relationship("Company")
    counterparty = relationship("Counterparty")
    warehouse = relationship("Warehouse")
    order = relationship("Order")
    created_by_user = relationship("User")
    lines = relationship("SalesInvoiceLine", back_populates="invoice", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<SalesInvoice {self.invoice_number} - {self.status}>"

class SalesInvoiceLine(BaseModel):
    """
    Sales Invoice Line model
    """
    __tablename__ = "sales_invoice_lines"
    
    quantity = Column(Numeric(15, 3), nullable=False)
    price = Column(Numeric(15, 2), nullable=False)
    total = Column(Numeric(15, 2), nullable=False)
    
    # Foreign Keys
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("sales_invoices.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("product_variants.id", ondelete="RESTRICT"), nullable=True)
    
    # Relationships
    invoice = relationship("SalesInvoice", back_populates="lines")
    product = relationship("Product")
    variant = relationship("ProductVariant")
    
    def __repr__(self):
        return f"<SalesInvoiceLine qty={self.quantity} price={self.price}>"
