from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from decimal import Decimal
from .base import BaseModel

class ProductVariant(BaseModel):
    """
    Specific product instances with different attributes (e.g., Sofa - Blue - Velvet)
    """
    __tablename__ = "product_variants"
    
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    sku = Column(String(100), nullable=False, index=True)
    
    # Overrides (if null, use product default)
    price_override = Column(Numeric(15, 2), nullable=True)
    cost_override = Column(Numeric(15, 2), nullable=True)
    
    image_url = Column(String(500), nullable=True)
    is_primary = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    product = relationship("Product", back_populates="variants")
    values = relationship("VariantValue", back_populates="variant", cascade="all, delete-orphan")

class VariantValue(BaseModel):
    """
    Specific value for a variant's attribute
    """
    __tablename__ = "variant_values"
    
    variant_id = Column(UUID(as_uuid=True), ForeignKey("product_variants.id", ondelete="CASCADE"), nullable=False)
    attribute_id = Column(UUID(as_uuid=True), ForeignKey("attributes.id", ondelete="CASCADE"), nullable=False)
    option_id = Column(UUID(as_uuid=True), ForeignKey("attribute_options.id", ondelete="SET NULL"), nullable=True)
    text_value = Column(String(255), nullable=True) # for TEXT or NUMBER types
    
    # Relationships
    variant = relationship("ProductVariant", back_populates="values")
    attribute = relationship("Attribute")
    option = relationship("AttributeOption")
