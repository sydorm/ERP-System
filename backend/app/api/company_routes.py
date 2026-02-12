from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.api.dependencies import get_db, get_current_user
from app.models.company import Company
from app.models.user import User
from app.schemas.company import CompanyCreate, CompanyResponse, CompanyUpdate
from app.services.tax_service import tax_service

router = APIRouter(prefix="/api/v1/companies", tags=["Companies"])

@router.get("/", response_model=List[CompanyResponse])
async def get_companies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all companies accessible to the user."""
    # For now, return all companies since multi-tenant logic is being implemented
    # Ideally, filter by user access
    return db.query(Company).all()

@router.get("/my", response_model=List[CompanyResponse])
async def get_my_companies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get companies owned/assigned to current user."""
    # Current implementation links user to one company, 
    # but we search for all companies where user is assigned
    return db.query(Company).filter(Company.id == current_user.company_id).all()

@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    company_in: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new company."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create companies")
    
    db_obj = Company(**company_in.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific company details."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

@router.patch("/{company_id}/set-default", response_model=CompanyResponse)
async def set_default_company(
    company_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Set a company as default for the user."""
    # Verify company exists
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Reset other defaults for this user (or globally for now)
    db.query(Company).update({Company.is_default: False})
    
    company.is_default = True
    db.commit()
    db.refresh(company)
    return company

@router.get("/{company_id}/fetch-tax-rates", response_model=CompanyResponse)
async def fetch_tax_rates(
    company_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetch 'official' tax rates and update company details."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    rates = tax_service.get_current_rates()
    company.tax_amount_esv = rates["tax_amount_esv"]
    company.military_tax_rate = rates["military_tax_rate"]
    company.last_tax_update = rates["last_update"]
    
    # If group 3, set single tax to 5%
    if company.tax_group == "GROUP_3":
        company.tax_rate_single = rates["tax_rate_single_3"]
    
    db.commit()
    db.refresh(company)
    return company
