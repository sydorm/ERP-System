import enum
from sqlalchemy import Column, String, Boolean, ForeignKey, Integer, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel

class AttributeType(str, enum.Enum):
    TEXT = "TEXT"
    SELECT = "SELECT"
    NUMBER = "NUMBER"
    COLOR = "COLOR"
    BOOLEAN = "BOOLEAN"

class Attribute(BaseModel):
    """
    Global attribute definition (e.g., Fabric, Material, Color)
    """
    __tablename__ = "attributes"
    
    name = Column(String(255), nullable=False)
    type = Column(Enum(AttributeType), nullable=False, default=AttributeType.TEXT)
    icon = Column(String(50), nullable=True) # e.g. "Aa", "palette", "list"
    description = Column(String(500), nullable=True)
    is_archived = Column(Boolean, default=False, nullable=False)
    
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    
    # Relationships
    options = relationship("AttributeOption", back_populates="attribute", cascade="all, delete-orphan")
    categories = relationship("CategoryAttribute", back_populates="attribute", cascade="all, delete-orphan")

class AttributeOption(BaseModel):
    """
    Predefined values for SELECT or COLOR attributes
    """
    __tablename__ = "attribute_options"
    
    attribute_id = Column(UUID(as_uuid=True), ForeignKey("attributes.id", ondelete="CASCADE"), nullable=False)
    value = Column(String(255), nullable=False) # e.g. "Velvet", "Red"
    color_code = Column(String(20), nullable=True) # Hex code for COLOR type
    sort_order = Column(Integer, default=0)
    
    # Relationships
    attribute = relationship("Attribute", back_populates="options")

class CategoryAttribute(BaseModel):
    """
    Links attributes to product categories (from DictionaryItem)
    """
    __tablename__ = "category_attributes"
    
    category_code = Column(String(255), nullable=False, index=True) # Matches PRODUCT_CATEGORY code
    attribute_id = Column(UUID(as_uuid=True), ForeignKey("attributes.id", ondelete="CASCADE"), nullable=False)
    is_required = Column(Boolean, default=False)
    
    # Relationships
    attribute = relationship("Attribute", back_populates="categories")
