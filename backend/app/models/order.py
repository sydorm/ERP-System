"""
Order models - represents customer orders and their line items
"""
from sqlalchemy import Column, String, Date, ForeignKey, Numeric, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from decimal import Decimal
from datetime import date
import enum
from .base import BaseModel


class OrderStatus(str, enum.Enum):
    """Order status enumeration"""
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Order(BaseModel):
    """
    Order model
    Represents a customer order
    """
    __tablename__ = "orders"
    
    # Order Information
    order_number = Column(String(50), nullable=False, unique=True, index=True)
    order_date = Column(Date, nullable=False, default=date.today)
    
    # Status
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.DRAFT)
    
    # Financial
    total_amount = Column(Numeric(15, 2), nullable=False, default=Decimal("0.00"))
    
    # Foreign Keys
    counterparty_id = Column(UUID(as_uuid=True), ForeignKey("counterparties.id", ondelete="RESTRICT"), nullable=False)
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id", ondelete="RESTRICT"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Relationships
    company = relationship("Company", back_populates="orders")
    counterparty = relationship("Counterparty", back_populates="orders")
    warehouse = relationship("Warehouse", back_populates="orders")
    created_by_user = relationship("User", back_populates="created_orders", foreign_keys=[created_by])
    lines = relationship("OrderLine", back_populates="order", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Order {self.order_number} - {self.status}>"


class OrderLine(BaseModel):
    """
    Order Line model
    Represents a single line item in an order
    """
    __tablename__ = "order_lines"
    
    # Line Information
    quantity = Column(Numeric(15, 3), nullable=False)
    price = Column(Numeric(15, 2), nullable=False)
    total = Column(Numeric(15, 2), nullable=False)
    
    # Foreign Keys
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    
    # Relationships
    order = relationship("Order", back_populates="lines")
    product = relationship("Product", back_populates="order_lines")
    
    def __repr__(self):
        return f"<OrderLine qty={self.quantity} price={self.price}>"
