"""
Calculator models - isolated tables for drawer price calculator
"""
from sqlalchemy import Column, String, Boolean, Integer, Numeric, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base


class CalcMaterial(Base):
    __tablename__ = "calc_materials"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    thickness_mm = Column(Integer, nullable=True)
    price_per_m2 = Column(Numeric(12, 2), nullable=False, default=0)
    unit = Column(String(20), nullable=False, default="м²")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CalcHardware(Base):
    __tablename__ = "calc_hardware"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    brand = Column(String(100), nullable=True)
    length_mm = Column(Integer, nullable=True)
    category = Column(String(100), nullable=False, default="направляючі")
    price_per_unit = Column(Numeric(12, 2), nullable=False, default=0)
    unit = Column(String(20), nullable=False, default="пара")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CalcService(Base):
    __tablename__ = "calc_services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    price = Column(Numeric(12, 2), nullable=False, default=0)
    unit = Column(String(50), nullable=False, default="шт")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CalcQuote(Base):
    __tablename__ = "calc_quotes"

    id = Column(Integer, primary_key=True, index=True)
    client_name = Column(String(255), nullable=True)
    input_json = Column(Text, nullable=False)
    result_json = Column(Text, nullable=False)
    total_price = Column(Numeric(12, 2), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
