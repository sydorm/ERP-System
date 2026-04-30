from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.api.dependencies import get_db, get_current_user
from app.models.company import Company
from app.models.user import User
from app.schemas.company import CompanyCreate, CompanyResponse, CompanyUpdate
from app.services.tax_service import tax_service

router = APIRouter(prefix="/companies", tags=["Companies"])

@router.get("", response_model=List[CompanyResponse])
async def get_companies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    import traceback as tb
    try:
        companies = db.query(Company).all()
        result = []
        for c in companies:
            try:
                result.append(CompanyResponse.model_validate(c))
            except Exception as ve:
                raise HTTPException(status_code=500, detail=f"Validation error on company {c.id}: {str(ve)}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {str(e)}\n{tb.format_exc()}")

@router.get("/my", response_model=List[CompanyResponse])
async def get_my_companies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get companies owned/assigned to current user."""
    # Current implementation links user to one company, 
    # but we search for all companies where user is assigned
    return db.query(Company).filter(Company.id == current_user.company_id).all()

@router.post("", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
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

@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: UUID,
    company_in: CompanyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update specific company details."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Only allow admins to edit OR users that belong to this company (depends on auth rules)
    # For now, we will allow update.
    update_data = company_in.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(company, field, value)
        
    db.commit()
    db.refresh(company)
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

@router.get("/default", response_model=CompanyResponse)
async def get_default_company(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the default company."""
    company = db.query(Company).filter(
        Company.is_default == True,
        Company.is_active == True
    ).first()
    if not company:
        company = db.query(Company).filter(Company.is_active == True).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.patch("/default/cost-method")
async def update_cost_method(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update the cost price calculation method for the default company."""
    company = db.query(Company).filter(Company.id == current_user.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    method = data.get("cost_method", "last_price")
    if method not in ("none", "last_price", "weighted_average"):
        raise HTTPException(status_code=422, detail="Invalid cost_method value")
    company.cost_method = method
    db.commit()
    return {"cost_method": company.cost_method}


@router.get("/default/accounts", response_model=List[dict])
async def get_default_company_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get bank accounts for the default company."""
    company = db.query(Company).filter(Company.is_default == True).first()
    if not company:
        company = db.query(Company).first()
    
    if not company:
        return []
    
    # Simple list of dicts for now
    return [{"id": str(acc.id), "iban": acc.iban, "bank_name": acc.bank_name, "is_primary": acc.is_primary} for acc in company.bank_accounts]
