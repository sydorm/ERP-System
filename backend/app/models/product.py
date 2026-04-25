"""
Product model - represents items/nomenclature
"""
from sqlalchemy import Column, String, Boolean, ForeignKey, Text, Numeric, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from decimal import Decimal
from .base import BaseModel


class ProductAttribute(BaseModel):
    """
    Links a product to specific attributes and defines behavior
    """
    __tablename__ = "product_attributes"
    
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    attribute_id = Column(UUID(as_uuid=True), ForeignKey("attributes.id", ondelete="CASCADE"), nullable=False)
    generates_sku = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    product = relationship("Product", back_populates="product_attributes")
    attribute = relationship("Attribute")


class Product(BaseModel):
    """
    Product model (Nomenclature)
    Represents an item that can be bought/sold
    """
    __tablename__ = "products"
    
    # Basic Information
    sku = Column(String(100), nullable=True, index=True)  # Stock Keeping Unit
    name = Column(String(500), nullable=False, index=True)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    
    # Classification
    category = Column(String(255), nullable=True, index=True)
    unit_of_measure = Column(String(50), nullable=False, default="шт")  # шт, кг, м, л
    
    # Pricing
    price = Column(Numeric(15, 2), nullable=False, default=Decimal("0.00"))  # Selling price
    currency = Column(String(3), nullable=False, default="UAH")
    cost = Column(Numeric(15, 2), nullable=True)  # Purchase cost
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False, server_default='false')
    
    # Dimensions and Weight
    length_cm = Column(Numeric(10, 2), nullable=True)
    width_cm = Column(Numeric(10, 2), nullable=True)
    height_cm = Column(Numeric(10, 2), nullable=True)
    weight_kg = Column(Numeric(10, 2), nullable=True)
    
    # Stock Management
    min_stock = Column(Numeric(15, 3), nullable=True, default=0.0)
    optimal_stock = Column(Numeric(15, 3), nullable=True, default=0.0)
    default_supplier_id = Column(UUID(as_uuid=True), ForeignKey("counterparties.id", ondelete="SET NULL"), nullable=True)
    delivery_days = Column(Integer, nullable=True, default=0)

    # Manufacturing Parameters
    production_time_hours = Column(Numeric(10, 2), nullable=True)
    complexity_code = Column(String(50), nullable=True)
    min_production_batch = Column(Integer, nullable=True, default=1)
    max_production_per_day = Column(Integer, nullable=True)
    special_production_conditions = Column(Text, nullable=True)

    # Performer Restrictions
    performer_restriction_type = Column(String(50), nullable=True, default='any_role') # 'any_role', 'specific_brigade', 'specific_master'
    restricted_brigade_id = Column(UUID(as_uuid=True), ForeignKey("brigades.id", ondelete="SET NULL"), nullable=True)
    restricted_employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="SET NULL"), nullable=True)

    # Foreign Keys
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="products")
    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")
    price_rule = relationship("ProductPriceRule", back_populates="product", uselist=False, cascade="all, delete-orphan")
    product_attributes = relationship("ProductAttribute", back_populates="product", cascade="all, delete-orphan")
    order_lines = relationship("OrderLine", back_populates="product")
    
    def __repr__(self):
        return f"<Product {self.sku}: {self.name}>"
