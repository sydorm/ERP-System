from sqlalchemy import Column, String, Boolean, ForeignKey, Integer, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel

class ProductSpecification(BaseModel):
    """
    Product Specification (BOM Header)
    Represents a specific recipe or bill of materials for a product.
    """
    __tablename__ = "product_specifications"
    
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False) # e.g., "Стандартна v1", "Економ"
    is_active = Column(Boolean, default=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    notes = Column(Text, nullable=True)
    
    # Relationships
    product = relationship("Product", backref="specifications")
    items = relationship("SpecificationItem", back_populates="specification", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Specification {self.name} for {self.product_id}>"

class SpecificationItem(BaseModel):
    """
    Specification Item (BOM Line)
    Represents a component and its quantity in a specification.
    """
    __tablename__ = "specification_items"
    
    specification_id = Column(UUID(as_uuid=True), ForeignKey("product_specifications.id", ondelete="CASCADE"), nullable=False, index=True)
    component_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False) # The component being used
    quantity = Column(Numeric(15, 4), nullable=False, default=1.0)
    unit_of_measure = Column(String(50), nullable=True) # Optional override
    notes = Column(String(500), nullable=True)
    
    # Relationships
    specification = relationship("ProductSpecification", back_populates="items")
    component = relationship("Product", foreign_keys=[component_id])

    def __repr__(self):
        return f"<SpecItem {self.component_id} x {self.quantity}>"
