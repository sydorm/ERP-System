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
