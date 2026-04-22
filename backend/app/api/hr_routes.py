from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.db.session import get_db
from app.models import Department, Employee, EmployeeRole, User, DictionaryItem
from app.schemas.hr import (
    DepartmentCreate, DepartmentUpdate, DepartmentResponse,
    EmployeeCreate, EmployeeUpdate, EmployeeResponse,
    EmployeeRoleCreate, EmployeeRoleResponse
)
from app.api.dependencies import get_current_active_user

router = APIRouter()

# --- Departments ---

@router.get("/departments", response_model=List[DepartmentResponse])
async def list_departments(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Department).filter(Department.company_id == current_user.company_id)
    if search:
        query = query.filter(Department.name.ilike(f"%{search}%"))
        
    objs = query.offset(skip).limit(limit).all()
    
    # Enrich with head name
    for obj in objs:
        if obj.head_id:
            head = db.query(Employee).filter(Employee.id == obj.head_id).first()
            if head:
                obj.head_name = head.full_name
                
    return objs

@router.post("/departments", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
async def create_department(
    dept_in: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    dept = Department(
        **dept_in.dict(),
        company_id=current_user.company_id
    )
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept

@router.get("/departments/{id}", response_model=DepartmentResponse)
async def get_department(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    dept = db.query(Department).filter(
        Department.id == id, 
        Department.company_id == current_user.company_id
    ).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    return dept

@router.put("/departments/{id}", response_model=DepartmentResponse)
async def update_department(
    id: UUID,
    dept_in: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    dept = db.query(Department).filter(
        Department.id == id, 
        Department.company_id == current_user.company_id
    ).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
        
    update_data = dept_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(dept, field, value)
        
    db.commit()
    db.refresh(dept)
    return dept


# --- Employees ---

@router.get("/employees", response_model=List[EmployeeResponse])
async def list_employees(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    department_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Employee).filter(
        Employee.company_id == current_user.company_id,
        Employee.is_deleted == False
    )
    
    if search:
        query = query.filter(Employee.full_name.ilike(f"%{search}%"))
    if department_id:
        query = query.filter(Employee.department_id == department_id)
        
    objs = query.offset(skip).limit(limit).all()
    
    # Enrich with names
    for obj in objs:
        if obj.department:
            obj.department_name = obj.department.name
        if obj.status:
            obj.status_name = obj.status.name
            
    return objs

@router.post("/employees", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    emp_in: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    emp_data = emp_in.dict(exclude={'roles'})
    emp = Employee(
        **emp_data,
        company_id=current_user.company_id
    )
    db.add(emp)
    db.flush() # Get emp.id
    
    for role_in in emp_in.roles:
        role = EmployeeRole(
            **role_in.dict(),
            employee_id=emp.id
        )
        db.add(role)
        
    db.commit()
    db.refresh(emp)
    return emp

@router.get("/employees/{id}", response_model=EmployeeResponse)
async def get_employee(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    emp = db.query(Employee).filter(
        Employee.id == id, 
        Employee.company_id == current_user.company_id
    ).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
        
    # Enrich roles and other fields
    emp.department_name = emp.department.name if emp.department else None
    emp.status_name = emp.status.name if emp.status else None
    
    for role in emp.roles:
        role.role_name = role.role_dict.name if role.role_dict else None
        role.role_type_name = role.role_type_dict.name if role.role_type_dict else None
        role.accrual_type_name = role.accrual_type_dict.name if role.accrual_type_dict else None
        
    return emp

@router.put("/employees/{id}", response_model=EmployeeResponse)
async def update_employee(
    id: UUID,
    emp_in: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    emp = db.query(Employee).filter(
        Employee.id == id, 
        Employee.company_id == current_user.company_id
    ).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
        
    update_data = emp_in.dict(exclude_unset=True, exclude={'roles'})
    for field, value in update_data.items():
        setattr(emp, field, value)
        
    # Sync roles if provided
    if emp_in.roles is not None:
        # Delete old roles
        db.query(EmployeeRole).filter(EmployeeRole.employee_id == id).delete()
        # Add new roles
        for role_in in emp_in.roles:
            role = EmployeeRole(
                **role_in.dict(),
                employee_id=emp.id
            )
            db.add(role)
            
    db.commit()
    db.refresh(emp)
    return await get_employee(id, db, current_user)

@router.delete("/employees/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    emp = db.query(Employee).filter(
        Employee.id == id, 
        Employee.company_id == current_user.company_id
    ).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
        
    emp.is_deleted = True
    db.commit()
    return None
