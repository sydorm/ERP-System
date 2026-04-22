from sqlalchemy import Column, String, Boolean, ForeignKey, Date, DateTime, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel

class Department(BaseModel):
    """
    Organization Departments (Production, Office, Warehouse etc.)
    """
    __tablename__ = "departments"

    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    
    # Link to the head of the department
    head_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="SET NULL"), nullable=True)
    
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    company = relationship("Company", backref="departments")
    head = relationship("Employee", foreign_keys=[head_id], post_update=True)
    employees = relationship("Employee", back_populates="department", foreign_keys="Employee.department_id")


class Employee(BaseModel):
    """
    Employee card with basic info and linked dictionary statuses
    """
    __tablename__ = "employees"

    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Primary data
    full_name = Column(String(255), nullable=False, index=True)
    position = Column(String(255), nullable=False) # Free-form position title
    
    # Department Link
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id", ondelete="RESTRICT"), nullable=False)
    
    # Classification Link (Dictionary)
    status_id = Column(UUID(as_uuid=True), ForeignKey("dictionary_items.id", ondelete="RESTRICT"), nullable=False)
    
    # Additional data
    phone = Column(String(50), nullable=True)
    birth_date = Column(Date, nullable=True)
    hire_date = Column(Date, nullable=True)
    photo_url = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)

    # Relationships
    company = relationship("Company", backref="employees")
    department = relationship("Department", back_populates="employees", foreign_keys=[department_id])
    status = relationship("DictionaryItem", foreign_keys=[status_id])
    roles = relationship("EmployeeRole", back_populates="employee", cascade="all, delete-orphan")


class EmployeeRole(BaseModel):
    """
    Roles and Rates assigned to an employee
    """
    __tablename__ = "employee_roles"

    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Classification Links (Dictionaries)
    role_id = Column(UUID(as_uuid=True), ForeignKey("dictionary_items.id", ondelete="RESTRICT"), nullable=False) # PRODUCTION_STAGE
    role_type_id = Column(UUID(as_uuid=True), ForeignKey("dictionary_items.id", ondelete="RESTRICT"), nullable=False) # ROLE_TYPE (Main/Secondary)
    accrual_type_id = Column(UUID(as_uuid=True), ForeignKey("dictionary_items.id", ondelete="RESTRICT"), nullable=False) # ACCRUAL_TYPE (Piecework, etc.)
    
    rate = Column(Numeric(precision=15, scale=2), default=0.0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    employee = relationship("Employee", back_populates="roles")
    role_dict = relationship("DictionaryItem", foreign_keys=[role_id])
    role_type_dict = relationship("DictionaryItem", foreign_keys=[role_type_id])
    accrual_type_dict = relationship("DictionaryItem", foreign_keys=[accrual_type_id])
