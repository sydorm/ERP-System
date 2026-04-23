from typing import List, Optional
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.db.session import get_db
from app.models import AttendanceRecord, PayrollTransaction, Employee, Department, User, DictionaryItem
from app.schemas.payroll import (
    AttendanceRecordResponse, AttendanceBulkUpsert,
    PayrollTransactionCreate, PayrollTransactionResponse,
    EmployeeBalanceResponse, PayrollSummaryItem, DepartmentSummaryItem
)
from app.api.dependencies import get_current_active_user

router = APIRouter()

def check_payroll_admin(user: User):
    if not (user.is_superuser or user.role == 'admin' or user.permissions.get('payroll.admin')):
        raise HTTPException(status_code=403, detail="Доступ лише для адміністраторів зарплат")

# --- Attendance ---

@router.get("/attendance", response_model=List[AttendanceRecordResponse])
async def get_attendance(
    start_date: date,
    end_date: date,
    department_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Determine permission/scope
    is_admin = current_user.is_superuser or current_user.role == 'admin' or current_user.permissions.get('payroll.admin')
    
    # Check if user is a shop head
    shop_head_dept_ids = []
    if current_user.employee_id:
        head_depts = db.query(Department).filter(Department.head_id == current_user.employee_id).all()
        shop_head_dept_ids = [d.id for d in head_depts]

    if not is_admin and not shop_head_dept_ids:
        # Managers/Workers don't see attendance for now as per TZ
        raise HTTPException(status_code=403, detail="Доступ заборонено")

    query = db.query(AttendanceRecord).join(Employee).filter(
        Employee.company_id == current_user.company_id,
        AttendanceRecord.date >= start_date,
        AttendanceRecord.date <= end_date
    )

    if not is_admin:
        # Restriction for shop head
        if department_id:
            if department_id not in shop_head_dept_ids:
                raise HTTPException(status_code=403, detail="Ви не маєте доступу до цього підрозділу")
            query = query.filter(Employee.department_id == department_id)
        else:
            query = query.filter(Employee.department_id.in_(shop_head_dept_ids))
    elif department_id:
        query = query.filter(Employee.department_id == department_id)

    records = query.all()
    # Populate status names
    for r in records:
        r.status_name = r.status.name if r.status else None
    return records

@router.post("/attendance/upsert", status_code=status.HTTP_201_CREATED)
async def upsert_attendance(
    bulk_in: AttendanceBulkUpsert,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Check permissions (only Admin or Shop Head for their dept)
    is_admin = current_user.is_superuser or current_user.role == 'admin' or current_user.permissions.get('payroll.admin')
    
    shop_head_dept_ids = []
    if current_user.employee_id:
        head_depts = db.query(Department).filter(Department.head_id == current_user.employee_id).all()
        shop_head_dept_ids = [d.id for d in head_depts]

    for rec in bulk_in.records:
        # Permission check per record
        emp = db.query(Employee).filter(Employee.id == rec.employee_id).first()
        if not emp: continue
        
        if not is_admin and emp.department_id not in shop_head_dept_ids:
            # Skip records for departments they don't lead
            continue

        existing = db.query(AttendanceRecord).filter(
            AttendanceRecord.employee_id == rec.employee_id,
            AttendanceRecord.date == rec.date
        ).first()

        if existing:
            existing.status_id = rec.status_id
            existing.notes = rec.notes
            existing.start_time = rec.start_time
            existing.end_time = rec.end_time
            existing.break_hours = rec.break_hours
            existing.actual_hours = rec.actual_hours
        else:
            new_rec = AttendanceRecord(
                employee_id=rec.employee_id,
                date=rec.date,
                status_id=rec.status_id,
                notes=rec.notes,
                start_time=rec.start_time,
                end_time=rec.end_time,
                break_hours=rec.break_hours,
                actual_hours=rec.actual_hours
            )
            db.add(new_rec)
            
    db.commit()
    return {"status": "ok"}


# --- Payroll ---

@router.get("/payroll/balance", response_model=List[EmployeeBalanceResponse])
async def get_payroll_balances(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    check_payroll_admin(current_user)
    
    employees = db.query(Employee).filter(
        Employee.company_id == current_user.company_id,
        Employee.is_deleted == False
    ).all()
    
    results = []
    for emp in employees:
        # Sum accruals (Positive amount, transaction_type='ACCRUAL')
        # Sum payments (Negative amount, transaction_type='PAYMENT')
        accrual_sum = db.query(func.sum(PayrollTransaction.amount)).filter(
            PayrollTransaction.employee_id == emp.id,
            PayrollTransaction.transaction_type == 'ACCRUAL'
        ).scalar() or 0
        
        payment_sum = db.query(func.sum(PayrollTransaction.amount)).filter(
            PayrollTransaction.employee_id == emp.id,
            PayrollTransaction.transaction_type == 'PAYMENT'
        ).scalar() or 0
        
        results.append(EmployeeBalanceResponse(
            employee_id=emp.id,
            full_name=emp.full_name,
            department_name=emp.department.name if emp.department else None,
            total_accrued=accrual_sum,
            total_paid=abs(payment_sum),
            balance=accrual_sum + payment_sum # payment_sum is negative
        ))
        
    return results

@router.get("/payroll/transactions", response_model=List[PayrollTransactionResponse])
async def list_payroll_transactions(
    employee_id: Optional[UUID] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    check_payroll_admin(current_user)
    
    query = db.query(PayrollTransaction).join(Employee).filter(
        Employee.company_id == current_user.company_id
    )
    
    if employee_id:
        query = query.filter(PayrollTransaction.employee_id == employee_id)
    if start_date:
        query = query.filter(PayrollTransaction.date >= start_date)
    if end_date:
        query = query.filter(PayrollTransaction.date <= end_date)
        
    objs = query.order_by(PayrollTransaction.date.desc()).all()
    
    for obj in objs:
        obj.category_name = obj.category.name if obj.category else None
        obj.creator_name = obj.creator.full_name if obj.creator else None
        obj.production_order_number = obj.production_order.order_number if obj.production_order else None
        
    return objs

@router.post("/payroll/transaction", response_model=PayrollTransactionResponse)
async def create_payroll_transaction(
    trans_in: PayrollTransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    check_payroll_admin(current_user)
    
    # Ensure amount sign matches type
    amount = trans_in.amount
    if trans_in.transaction_type == 'ACCRUAL' and amount < 0:
        amount = abs(amount)
    elif trans_in.transaction_type == 'PAYMENT' and amount > 0:
        amount = -amount
        
    db_trans = PayrollTransaction(
        **trans_in.dict(exclude={'amount'}),
        amount=amount,
        created_by=current_user.id
    )
    db.add(db_trans)
    db.commit()
    db.refresh(db_trans)
    return db_trans

# --- Reports ---

@router.get("/reports/summary", response_model=List[PayrollSummaryItem])
async def get_payroll_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    check_payroll_admin(current_user)
    
    # Group transactions by month
    from sqlalchemy import extract
    
    # Query for accruals
    accruals = db.query(
        func.to_char(PayrollTransaction.date, 'YYYY-MM').label('month'),
        func.sum(PayrollTransaction.amount).label('total')
    ).join(Employee).filter(
        Employee.company_id == current_user.company_id,
        PayrollTransaction.transaction_type == 'ACCRUAL'
    ).group_by('month').all()
    
    # Query for payments
    payments = db.query(
        func.to_char(PayrollTransaction.date, 'YYYY-MM').label('month'),
        func.sum(PayrollTransaction.amount).label('total')
    ).join(Employee).filter(
        Employee.company_id == current_user.company_id,
        PayrollTransaction.transaction_type == 'PAYMENT'
    ).group_by('month').all()
    
    # Merge results
    summary_dict = {}
    for m, val in accruals:
        if m not in summary_dict: summary_dict[m] = {'accrued': 0, 'paid': 0}
        summary_dict[m]['accrued'] = val
        
    for m, val in payments:
        if m not in summary_dict: summary_dict[m] = {'accrued': 0, 'paid': 0}
        summary_dict[m]['paid'] = abs(val) # payment_sum is negative in DB
        
    results = [
        PayrollSummaryItem(period=m, total_accrued=data['accrued'], total_paid=data['paid'])
        for m, data in sorted(summary_dict.items(), reverse=True)
    ]
    return results

@router.get("/reports/by-department", response_model=List[DepartmentSummaryItem])
async def get_payroll_by_department(
    month: Optional[str] = None, # YYYY-MM
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    check_payroll_admin(current_user)
    
    query = db.query(
        Department.name.label('dept_name'),
        func.sum(PayrollTransaction.amount).label('amount'),
        PayrollTransaction.transaction_type
    ).join(Employee, Employee.department_id == Department.id)\
     .join(PayrollTransaction, PayrollTransaction.employee_id == Employee.id)\
     .filter(Employee.company_id == current_user.company_id)
     
    if month:
        query = query.filter(func.to_char(PayrollTransaction.date, 'YYYY-MM') == month)
        
    results = query.group_by(Department.name, PayrollTransaction.transaction_type).all()
    
    dept_dict = {}
    for name, amount, t_type in results:
        if name not in dept_dict: dept_dict[name] = {'accrued': 0, 'paid': 0}
        if t_type == 'ACCRUAL':
            dept_dict[name]['accrued'] += amount
        else:
            dept_dict[name]['paid'] += abs(amount)
            
    return [
        DepartmentSummaryItem(department_name=name, total_accrued=data['accrued'], total_paid=data['paid'])
        for name, data in dept_dict.items()
    ]
