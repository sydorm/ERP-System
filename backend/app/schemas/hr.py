from datetime import date, datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal

# --- Employee Role ---

class EmployeeRoleBase(BaseModel):
    role_id: UUID
    role_type_id: UUID
    accrual_type_id: UUID
    rate: Decimal = Field(default=0.0, ge=0)
    is_active: bool = True

class EmployeeRoleCreate(EmployeeRoleBase):
    pass

class EmployeeRoleUpdate(BaseModel):
    role_id: Optional[UUID] = None
    role_type_id: Optional[UUID] = None
    accrual_type_id: Optional[UUID] = None
    rate: Optional[Decimal] = Field(None, ge=0)
    is_active: Optional[bool] = None

class EmployeeRoleResponse(EmployeeRoleBase):
    id: UUID
    employee_id: UUID
    
    # Optional names for easier display
    role_name: Optional[str] = None
    role_type_name: Optional[str] = None
    accrual_type_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# --- Department ---

class DepartmentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    head_id: Optional[UUID] = None
    is_active: bool = True

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    head_id: Optional[UUID] = None
    is_active: Optional[bool] = None

class DepartmentResponse(DepartmentBase):
    id: UUID
    company_id: UUID
    head_name: Optional[str] = None # Helper for list view

    model_config = ConfigDict(from_attributes=True)

# --- Employee ---

class EmployeeBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=255)
    position: Optional[str] = Field(None, max_length=255)
    department_id: UUID
    status_id: UUID
    
    phone: Optional[str] = Field(None, max_length=50)
    birth_date: Optional[date] = None
    hire_date: Optional[date] = None
    photo_url: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None

class EmployeeCreate(EmployeeBase):
    roles: List[EmployeeRoleCreate] = []

class EmployeeUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    position: Optional[str] = Field(None, max_length=255)
    department_id: Optional[UUID] = None
    status_id: Optional[UUID] = None
    
    phone: Optional[str] = Field(None, max_length=50)
    birth_date: Optional[date] = None
    hire_date: Optional[date] = None
    photo_url: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None
    
    roles: Optional[List[EmployeeRoleCreate]] = None # Overwrite roles on update for simplicity in v1

class EmployeeResponse(EmployeeBase):
    id: UUID
    company_id: UUID
    is_deleted: bool
    
    department_name: Optional[str] = None
    status_name: Optional[str] = None
    
    roles: List[EmployeeRoleResponse] = []

    model_config = ConfigDict(from_attributes=True)
