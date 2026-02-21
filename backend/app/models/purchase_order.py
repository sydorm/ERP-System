from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
import datetime
from .base import BaseModel

class PurchaseOrderStatus(str, enum.Enum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    DONE = "done"
    CANCELLED = "cancelled"

class PurchaseOrder(BaseModel):
    """
    Purchase Order (Замовлення постачальнику)
    """
    __tablename__ = "purchase_orders"
    
    order_number = Column(String(50), nullable=False, index=True)
    order_date = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    expected_date = Column(DateTime, nullable=True)
    
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("counterparties.id"), nullable=False)
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=False)
    
    status = Column(Enum(PurchaseOrderStatus, values_callable=lambda obj: [e.value for e in obj]), default=PurchaseOrderStatus.DRAFT, nullable=False)
    currency = Column(String(3), nullable=False, default="UAH")
    total_amount = Column(Numeric(15, 2), nullable=False, default=0.0)
    notes = Column(Text, nullable=True)
    
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Relationships
    lines = relationship("PurchaseOrderLine", back_populates="purchase_order", cascade="all, delete-orphan")
    supplier = relationship("Counterparty", foreign_keys=[supplier_id])
    warehouse = relationship("Warehouse", foreign_keys=[warehouse_id])
    company = relationship("Company")

class PurchaseOrderLine(BaseModel):
    """
    Purchase Order Line
    """
    __tablename__ = "purchase_order_lines"
    
    order_id = Column(UUID(as_uuid=True), ForeignKey("purchase_orders.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("product_variants.id"), nullable=True)
    
    quantity = Column(Numeric(15, 4), nullable=False, default=1.0)
    price = Column(Numeric(15, 2), nullable=False, default=0.0)
    total = Column(Numeric(15, 2), nullable=False, default=0.0)
    
    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="lines")
    product = relationship("Product")
    variant = relationship("ProductVariant")
