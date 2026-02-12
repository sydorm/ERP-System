"""
Company model - represents businesses (FOP/TOV)
"""
from sqlalchemy import Column, String, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship
import enum
from .base import BaseModel


class CompanyType(str, enum.Enum):
    """Company type enumeration"""
    FOP = "FOP"  # ФОП (Фізична особа підприємець)
    TOV = "TOV"  # ТОВ (Товариство з обмеженою відповідальністю)


class TaxGroup(str, enum.Enum):
    """Tax group enumeration"""
    GROUP_1 = "GROUP_1"  # 1 група (ФОП)
    GROUP_2 = "GROUP_2"  # 2 група (ФОП)
    GROUP_3 = "GROUP_3"  # 3 група (ФОП/ТОВ)
    GENERAL = "GENERAL"  # Загальна система


class Company(BaseModel):
    """
    Company model
    Represents a business entity (FOP or LLC) with full legal details
    """
    __tablename__ = "companies"
    
    # Basic Information / Основна інформація
    name = Column(String(255), nullable=False, index=True) # Internal name / Назва для відображення
    full_name_uk = Column(String(500), nullable=True)      # Full legal name in Ukrainian / Повна назва укр
    short_name_uk = Column(String(255), nullable=True)     # Short legal name in Ukrainian / Скорочена назва укр
    full_name_en = Column(String(500), nullable=True)      # Full name in English / Назва англ.
    website = Column(String(255), nullable=True)           # Website / Сайт
    
    # Legal Details / Реєстраційні дані
    edrpou = Column(String(20), nullable=True, index=True) # EDRPOU code / ЄДРПОУ або РНОКПП (10 digits for FOP, 8 for TOV)
    ipn = Column(String(20), nullable=True)                # Tax ID / ІПН (12 digits)
    kved = Column(String(10), nullable=True)               # Main KVED code / Основний КВЕД (e.g., 62.01)
    
    # Signatories / Підписанти
    director_name = Column(String(255), nullable=True)     # Director Name / ПІБ Керівника
    director_position = Column(String(100), nullable=True) # Director Position / Посада (Директор, Генеральний директор)
    accountant_name = Column(String(255), nullable=True)   # Accountant Name / ПІБ Бухгалтера
    
    # Addresses / Адреси
    legal_address = Column(String(500), nullable=True)     # Legal Address / Юридична адреса
    physical_address = Column(String(500), nullable=True)  # Physical Address / Фактична адреса
    
    # Contact Info / Контакти
    phone = Column(String(50), nullable=True)              # Phone / Телефон
    email = Column(String(255), nullable=True)             # Email / Електронна пошта
    
    # Tax Settings / Податкові налаштування
    company_type = Column(Enum(CompanyType), nullable=False, default=CompanyType.FOP)
    tax_group = Column(Enum(TaxGroup), nullable=True)      # Tax Group / Група оподаткування
    vat_payer = Column(Boolean, default=False)             # VAT Payer / Платник ПДВ
    vat_number = Column(String(50), nullable=True)         # VAT Number / Номер свідоцтва ПДВ (Optional, usually IPN is used)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    users = relationship("User", back_populates="company", cascade="all, delete-orphan")
    warehouses = relationship("Warehouse", back_populates="company", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="company", cascade="all, delete-orphan")
    counterparties = relationship("Counterparty", back_populates="company", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="company", cascade="all, delete-orphan")
    bank_accounts = relationship("BankAccount", back_populates="company", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Company {self.name} ({self.company_type})>"
