"""
Dictionary model - represents generic system lists (UOMs, Statuses, etc.)
"""
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel

class DictionaryItem(BaseModel):
    """
    Generic Dictionary Item
    Stores values for various system lists (Units, Categories, Statuses)
    """
    __tablename__ = "dictionary_items"
    
    # Scope
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Classification
    category = Column(String(50), nullable=False, index=True) # e.g., 'UOM', 'PRODUCT_CATEGORY', 'ORDER_STATUS'
    
    # Data
    code = Column(String(50), nullable=False) # e.g., 'kg', 'new'
    name = Column(String(255), nullable=False) # e.g., 'Kilogram', 'New Order'
    
    # UI props
    color = Column(String(20), nullable=True) # e.g., 'success', '#f00' (for badges)
    icon = Column(String(50), nullable=True) # e.g., 'Box', 'Check'
    sort_order = Column(Integer, default=0, nullable=False)
    
    # System logic
    is_fixed = Column(Boolean, default=False, nullable=False) # If True, cannot be deleted (system default)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    company = relationship("Company", backref="dictionary_items")
    
    def __repr__(self):
        return f"<DictItem {self.category}:{self.code}>"
