"""
Company model - represents businesses (FOP/TOV)
"""
from sqlalchemy import Column, String, Boolean, Enum
from sqlalchemy.orm import relationship
import enum
from .base import BaseModel


class CompanyType(str, enum.Enum):
    """Company type enumeration"""
    FOP = "FOP"  # ФОП (Фізична особа підприємець)
    TOV = "TOV"  # ТОВ (Товариство з обмеженою відповідальністю)


class Company(BaseModel):
    """
    Company model
    Represents a business entity (FOP or LLC)
    """
    __tablename__ = "companies"
    
    # Basic Information
    name = Column(String(255), nullable=False, index=True)
    legal_name = Column(String(500), nullable=False)
    tax_id = Column(String(50), nullable=False, unique=True, index=True)  # ЄДРПОУ or ІПН
    company_type = Column(Enum(CompanyType), nullable=False, default=CompanyType.FOP)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    users = relationship("User", back_populates="company", cascade="all, delete-orphan")
    warehouses = relationship("Warehouse", back_populates="company", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="company", cascade="all, delete-orphan")
    counterparties = relationship("Counterparty", back_populates="company", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="company", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Company {self.name} ({self.company_type})>"
