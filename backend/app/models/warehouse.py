"""
Warehouse model - represents storage locations
"""
from sqlalchemy import Column, String, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel


class Warehouse(BaseModel):
    """
    Warehouse model
    Represents a physical storage location
    """
    __tablename__ = "warehouses"
    
    # Basic Information
    name = Column(String(255), nullable=False, index=True)
    address = Column(Text, nullable=True)
    
    # Status
    is_default = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Foreign Keys
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="warehouses")
    orders = relationship("Order", back_populates="warehouse")
    
    def __repr__(self):
        return f"<Warehouse {self.name}>"
