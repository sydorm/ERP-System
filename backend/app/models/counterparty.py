"""
Counterparty model - represents customers and suppliers
"""
from sqlalchemy import Column, String, Boolean, ForeignKey, Integer, Text, Numeric, func
from sqlalchemy.dialects import postgresql
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
    default_contract = Column(String(255), nullable=True)
    
    # Customer specific
    acquisition_channel_id = Column(UUID(as_uuid=True), ForeignKey("dictionary_items.id", ondelete="SET NULL"), nullable=True)
    city = Column(String(255), nullable=True)
    np_department = Column(String(255), nullable=True)
    discount_percent = Column(Integer, nullable=True, default=0)
    notes = Column(Text, nullable=True)
    tags = Column(postgresql.JSONB, nullable=True)  # Using JSONB for tags
    
    # Supplier specific
    delivery_days = Column(Integer, nullable=True, default=0)
    payment_terms_id = Column(UUID(as_uuid=True), ForeignKey("dictionary_items.id", ondelete="SET NULL"), nullable=True)
    payment_terms = Column(String(255), nullable=True)
    min_order_amount = Column(Numeric(15, 2), nullable=True, default=0.0)
    contact_person = Column(String(255), nullable=True)
    supplied_materials = Column(Text, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False, server_default='false')
    
    # Foreign Keys
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="counterparties")
    orders = relationship("Order", back_populates="counterparty")
    acquisition_channel = relationship("DictionaryItem", foreign_keys=[acquisition_channel_id])
    payment_terms_item = relationship("DictionaryItem", foreign_keys=[payment_terms_id])
    
    def __repr__(self):
        type_str = []
        if self.is_customer:
            type_str.append("Клієнт")
        if self.is_supplier:
            type_str.append("Постачальник")
        return f"<Counterparty {self.name} ({', '.join(type_str)})>"


class CounterpartyBankAccount(BaseModel):
    __tablename__ = "counterparty_bank_accounts"
    
    counterparty_id = Column(UUID(as_uuid=True), ForeignKey("counterparties.id", ondelete="CASCADE"), nullable=False, index=True)
    bank_name = Column(String(255), nullable=True)
    iban = Column(String(50), nullable=False)
    currency = Column(String(10), default="UAH")
    purpose = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    
    counterparty = relationship("Counterparty", backref="bank_accounts")


class CounterpartyContact(BaseModel):
    __tablename__ = "counterparty_contacts"
    
    counterparty_id = Column(UUID(as_uuid=True), ForeignKey("counterparties.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    position = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    telegram = Column(String(100), nullable=True)
    email = Column(String(255), nullable=True)
    is_primary = Column(Boolean, default=False)
    
    counterparty = relationship("Counterparty", backref="contacts")


class CounterpartyMaterial(BaseModel):
    __tablename__ = "counterparty_materials"
    
    counterparty_id = Column(UUID(as_uuid=True), ForeignKey("counterparties.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    price = Column(Numeric(15, 2), nullable=False, default=0.0)
    currency = Column(String(10), default="UAH")
    
    counterparty = relationship("Counterparty", backref="materials")
    product = relationship("Product")


class CounterpartyDocument(BaseModel):
    __tablename__ = "counterparty_documents"
    
    counterparty_id = Column(UUID(as_uuid=True), ForeignKey("counterparties.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    file_url = Column(String(1000), nullable=False)
    created_at = Column(postgresql.TIMESTAMP, server_default=func.now())
    
    counterparty = relationship("Counterparty", backref="documents")
