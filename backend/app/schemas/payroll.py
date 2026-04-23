from datetime import date
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal

# --- Attendance ---

class AttendanceRecordBase(BaseModel):
    employee_id: UUID
    date: date
    status_id: UUID
    start_time: Optional[str] = Field(None, max_length=5)
    end_time: Optional[str] = Field(None, max_length=5)
    break_hours: Optional[Decimal] = Decimal("1.0")
    actual_hours: Optional[Decimal] = Decimal("0.0")
    notes: Optional[str] = Field(None, max_length=255)

class AttendanceRecordCreate(AttendanceRecordBase):
    pass

class AttendanceRecordResponse(AttendanceRecordBase):
    id: UUID
    status_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class AttendanceUpsert(BaseModel):
    employee_id: UUID
    date: date
    status_id: UUID
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    break_hours: Optional[Decimal] = None
    actual_hours: Optional[Decimal] = None
    notes: Optional[str] = None

class AttendanceBulkUpsert(BaseModel):
    records: List[AttendanceUpsert]

# --- Payroll transactions ---

class PayrollTransactionBase(BaseModel):
    employee_id: UUID
    amount: Decimal = Field(..., ge=-999999999, le=999999999)
    transaction_type: str = Field(..., pattern="^(ACCRUAL|PAYMENT)$")
    date: date
    category_id: UUID
    production_order_id: Optional[UUID] = None
    description: Optional[str] = Field(None, max_length=500)

class PayrollTransactionCreate(PayrollTransactionBase):
    pass

class PayrollTransactionResponse(PayrollTransactionBase):
    id: UUID
    category_name: Optional[str] = None
    creator_name: Optional[str] = None
    production_order_number: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# --- Summary / Balance ---

class EmployeeBalanceResponse(BaseModel):
    employee_id: UUID
    full_name: str
    department_name: Optional[str] = None
    total_accrued: Decimal
    total_paid: Decimal
    balance: Decimal

    model_config = ConfigDict(from_attributes=True)

# --- Reporting ---

class PayrollSummaryItem(BaseModel):
    period: str  # e.g. "2024-04"
    total_accrued: Decimal
    total_paid: Decimal

class DepartmentSummaryItem(BaseModel):
    department_name: str
    total_accrued: Decimal
    total_paid: Decimal
