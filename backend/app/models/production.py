import uuid
from sqlalchemy import Column, String, Text, ForeignKey, Numeric, DateTime, Enum, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import BaseModel

class ProductionOrder(BaseModel):
    """
    Production Order (Завдання на виробництво)
    Document that initiates the manufacturing of products.
    """
    __tablename__ = "production_orders"
    
    # Document info
    order_number = Column(String(50), nullable=False, unique=True, index=True)
    order_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    due_date = Column(DateTime, nullable=True)
    status = Column(String(50), nullable=False, default="draft", index=True)  # draft, released, in_progress, completed, cancelled
    
    # Multi-link for source & client
    source_type = Column(String(20), nullable=False, default="quick") # crm, quick
    source_id = Column(UUID(as_uuid=True), nullable=True) # Reference to CRM order if type is crm
    client_id = Column(UUID(as_uuid=True), ForeignKey("counterparties.id", ondelete="SET NULL"), nullable=True)
    priority = Column(String(20), nullable=False, default="normal") # normal, urgent, critical

    # Relationships to other docs
    base_order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="SET NULL"), nullable=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id", ondelete="RESTRICT"), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    comment = Column(Text, nullable=True)
    
    # Revisions / Tracking
    completed_at = Column(DateTime, nullable=True)
    
    # Relations
    company = relationship("Company")
    warehouse = relationship("Warehouse")
    creator = relationship("User")
    base_order = relationship("Order")
    client = relationship("Counterparty")
    
    lines = relationship("ProductionOrderLine", back_populates="production_order", cascade="all, delete-orphan")
    materials = relationship("ProductionOrderMaterial", back_populates="production_order", cascade="all, delete-orphan")
    assignments = relationship("ProductionOrderWorkerAssignment", back_populates="production_order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ProductionOrder {self.order_number}>"


class ProductionOrderLine(BaseModel):
    """
    Line items to manufacture (Products to be produced).
    """
    __tablename__ = "production_order_lines"
    
    production_order_id = Column(UUID(as_uuid=True), ForeignKey("production_orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("product_variants.id", ondelete="SET NULL"), nullable=True)
    specification_id = Column(UUID(as_uuid=True), ForeignKey("product_specifications.id", ondelete="SET NULL"), nullable=True)
    
    quantity = Column(Numeric(15, 3), nullable=False, default=1)
    produced_quantity = Column(Numeric(15, 3), nullable=False, default=0)
    
    production_order = relationship("ProductionOrder", back_populates="lines")
    product = relationship("Product")
    variant = relationship("ProductVariant")
    specification = relationship("ProductSpecification")

    def __repr__(self):
        return f"<ProductionOrderLine {self.product_id} qty={self.quantity}>"


class ProductionOrderMaterial(BaseModel):
    """
    Raw materials required to fulfill the production order.
    Generated from BOM but can be manually modified.
    """
    __tablename__ = "production_order_materials"
    
    production_order_id = Column(UUID(as_uuid=True), ForeignKey("production_orders.id", ondelete="CASCADE"), nullable=False)
    component_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    
    # Grouping info (e.g., from which line this requirement came from, optional if we aggregate)
    # But usually it's just aggregated for the whole document
    
    required_quantity = Column(Numeric(15, 4), nullable=False)
    issued_quantity = Column(Numeric(15, 4), nullable=False, default=0)
    unit_of_measure = Column(String(50), nullable=True)
    
    cost_estimate = Column(Numeric(15, 2), nullable=True) # Estimated cost of the material
    
    production_order = relationship("ProductionOrder", back_populates="materials")
    component = relationship("Product")

    def __repr__(self):
        return f"<ProductionOrderMaterial {self.component_id} req={self.required_quantity}>"


class ProductionOrderWorkerAssignment(BaseModel):
    """
    Workers assigned to specific stages of a production order.
    Used for automated payroll accruals.
    """
    __tablename__ = "production_order_assignments"

    production_order_id = Column(UUID(as_uuid=True), ForeignKey("production_orders.id", ondelete="CASCADE"), nullable=False)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=True)
    
    # Stage Link (from PRODUCTION_STAGE dictionary)
    stage_id = Column(UUID(as_uuid=True), ForeignKey("dictionary_items.id", ondelete="RESTRICT"), nullable=False)
    brigade_id = Column(UUID(as_uuid=True), ForeignKey("brigades.id", ondelete="SET NULL"), nullable=True)
    
    # How much did they produce (defaults to order qty if null)
    quantity = Column(Numeric(15, 3), nullable=True)
    planned_hours = Column(Numeric(15, 2), nullable=False, default=0.0)
    status = Column(String(20), nullable=False, default="pending") # pending, in_progress, completed

    # Relations
    production_order = relationship("ProductionOrder", back_populates="assignments")
    employee = relationship("Employee")
    stage = relationship("DictionaryItem")
