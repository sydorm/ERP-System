"""
Order models - represents customer orders and their line items
"""
from sqlalchemy import Column, String, Date, ForeignKey, Numeric, Enum, Text, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
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
    shipping_date = Column(Date, nullable=True)

    # Status (fulfillment state)
    status = Column(String(50), nullable=False, default="draft")

    # CRM pipeline stage (separate from fulfillment status)
    crm_stage = Column(String(50), nullable=False, default="new", index=True)

    # CRM: client context
    channel = Column(String(50), nullable=True)          # instagram/website/referral/telegram/olx/phone
    city = Column(String(255), nullable=True)
    delivery_type = Column(String(50), nullable=True)    # nova_poshta/ukrposhta/courier/pickup

    # CRM: product characteristics selected by client (JSON)
    attributes_values = Column(JSONB, nullable=True)

    # CRM: financial
    paid_amount = Column(Numeric(15, 2), nullable=False, default=Decimal("0.00"))
    payment_status = Column(String(50), nullable=False, default="unpaid", index=True)
    prepayment_percent = Column(Numeric(5, 2), nullable=True)
    prepayment_amount = Column(Numeric(15, 2), nullable=True)

    # CRM: dates
    deadline_date = Column(Date, nullable=True)
    next_contact_date = Column(Date, nullable=True)

    # CRM: production
    # CRM: priority
    priority = Column(String(20), nullable=False, default="normal")  # low/normal/urgent/critical
    priority_id = Column(UUID(as_uuid=True), ForeignKey("dictionary_items.id", ondelete="SET NULL"), nullable=True)
    
    # CRM: foreign keys to dictionaries
    lead_source_id = Column(UUID(as_uuid=True), ForeignKey("dictionary_items.id", ondelete="SET NULL"), nullable=True)
    cancel_reason_id = Column(UUID(as_uuid=True), ForeignKey("dictionary_items.id", ondelete="SET NULL"), nullable=True)
    delivery_method_id = Column(UUID(as_uuid=True), ForeignKey("dictionary_items.id", ondelete="SET NULL"), nullable=True)
    client_type_id = Column(UUID(as_uuid=True), ForeignKey("dictionary_items.id", ondelete="SET NULL"), nullable=True)
    payment_status_id = Column(UUID(as_uuid=True), ForeignKey("dictionary_items.id", ondelete="SET NULL"), nullable=True)
    bank_account_id = Column(UUID(as_uuid=True), ForeignKey("bank_accounts.id", ondelete="SET NULL"), nullable=True)

    manager_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)


    # CRM: communication tracking
    contact_attempts = Column(Integer, nullable=False, default=0)
    next_contact_at = Column(DateTime, nullable=True)

    # CRM: notes & media
    internal_notes = Column(Text, nullable=True)
    reference_photo = Column(String(500), nullable=True)

    # Contract & notes
    contract = Column(String(255), nullable=True)
    comment = Column(Text, nullable=True)

    # Financial
    total_amount = Column(Numeric(15, 2), nullable=False, default=Decimal("0.00"))
    discount_percent = Column(Numeric(5, 2), nullable=True, default=Decimal("0.00"))

    # Foreign Keys
    counterparty_id = Column(UUID(as_uuid=True), ForeignKey("counterparties.id", ondelete="RESTRICT"), nullable=False)
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id", ondelete="RESTRICT"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    company = relationship("Company", back_populates="orders")
    counterparty = relationship("Counterparty", back_populates="orders")
    warehouse = relationship("Warehouse", back_populates="orders")
    created_by_user = relationship("User", back_populates="created_orders", foreign_keys=[created_by], overlaps="manager")
    manager = relationship("User", foreign_keys=[manager_id], overlaps="created_by_user,created_orders")
    lines = relationship("OrderLine", back_populates="order", cascade="all, delete-orphan")
    contacts = relationship("CrmContact", back_populates="order", cascade="all, delete-orphan")
    tasks = relationship("CrmTask", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Order {self.order_number} - {self.crm_stage}>"


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
    variant_id = Column(UUID(as_uuid=True), ForeignKey("product_variants.id", ondelete="SET NULL"), nullable=True)
    specification_id = Column(UUID(as_uuid=True), ForeignKey("product_specifications.id", ondelete="SET NULL"), nullable=True)
    
    # Relationships
    order = relationship("Order", back_populates="lines")
    product = relationship("Product", back_populates="order_lines")
    variant = relationship("ProductVariant")
    specification = relationship("ProductSpecification")
    
    def __repr__(self):
        return f"<OrderLine qty={self.quantity} price={self.price}>"
