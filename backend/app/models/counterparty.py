"""
Counterparty model - represents customers and suppliers
"""
from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel


class Counterparty(BaseModel):
    """
    Counterparty model
    Represents a business partner (customer or supplier)
    """
    __tablename__ = "counterparties"
    
    # Basic Information
    name = Column(String(255), nullable=False, index=True)
    legal_name = Column(String(500), nullable=True)
    tax_id = Column(String(50), nullable=True, index=True)  # ЄДРПОУ or ІПН
    
    # Type flags
    is_customer = Column(Boolean, default=True, nullable=False)
    is_supplier = Column(Boolean, default=False, nullable=False)
    
    # Contact Information
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    address = Column(String(500), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Foreign Keys
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="counterparties")
    orders = relationship("Order", back_populates="counterparty")
    
    def __repr__(self):
        type_str = []
        if self.is_customer:
            type_str.append("Клієнт")
        if self.is_supplier:
            type_str.append("Постачальник")
        return f"<Counterparty {self.name} ({', '.join(type_str)})>"
