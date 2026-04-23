"""
Supplier Price model - links products to suppliers and their specific prices
"""
from sqlalchemy import Column, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel


class SupplierPrice(BaseModel):
    """
    Supplier Price model
    Stores price for a specific product from a specific supplier
    """
    __tablename__ = "supplier_prices"
    
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("counterparties.id", ondelete="CASCADE"), nullable=False, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    
    price = Column(Numeric(15, 2), nullable=False, default=0.0)
    
    # Relationships
    product = relationship("Product")
    supplier = relationship("Counterparty")
    company = relationship("Company")

    def __repr__(self):
        return f"<SupplierPrice Product={self.product_id} Supplier={self.supplier_id} Price={self.price}>"
