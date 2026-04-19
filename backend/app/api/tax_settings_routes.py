from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime

from app.api.dependencies import get_db, get_current_user
from app.models.company import Company
from app.schemas.tax import TaxSettingsUpdate
from app.services.anthropic_service import anthropic_service

router = APIRouter(prefix="/organization", tags=["Organization"])

@router.get("/tax-settings")
def get_tax_settings(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get current taxation settings for the organization."""
    # For now, we assume there's one default company per setup
    company = db.query(Company).filter(Company.is_default == True).first()
    if not company:
        company = db.query(Company).first()
    
    if not company:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    return {
        "company_id": str(company.id),
        "tax_group": company.tax_group,
        "vat_payer": company.vat_payer,
        "tax_settings": company.tax_settings or {
            "tax_year": 2026,
            "min_wage": 8647,
            "subsistence_min": 3328,
            "esv_rate": 0.22,
            "single_tax_rate": 0.20,
            "military_levy_rate": 0.10,
            "limit_multiplier_g1": 167,
            "limit_multiplier_g2": 834,
            "limit_multiplier_g3": 1167,
            "last_updated": None
        }
    }

@router.put("/tax-settings")
def update_tax_settings(
    data: TaxSettingsUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Save updated taxation settings."""
    company = db.query(Company).filter(Company.is_default == True).first()
    if not company:
        company = db.query(Company).first()
    
    if not company:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Update main company fields if they are in the settings
    if "tax_group" in data.settings:
        company.tax_group = data.settings["tax_group"]
    if "vat_payer" in data.settings:
        company.vat_payer = data.settings["vat_payer"]
    
    # Update JSON settings
    current_settings = company.tax_settings or {}
    current_settings.update(data.settings)
    company.tax_settings = current_settings
    
    db.commit()
    db.refresh(company)
    return {"status": "success", "settings": company.tax_settings}

@router.post("/tax-settings/refresh")
async def refresh_tax_settings(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Fetch latest tax rates using AI and return them (without saving)."""
    company = db.query(Company).filter(Company.is_default == True).first()
    if not company:
        company = db.query(Company).first()
    
    tax_group = company.tax_group.name if company and company.tax_group else "GROUP_2"
    
    # Try to refresh using AI
    new_data = await anthropic_service.get_tax_rates(tax_group=tax_group, year=2026)
    
    # Update last_updated but don't save to DB yet (user needs to click Save in UI)
    new_data["last_updated"] = datetime.now().isoformat()
    
    return {"status": "success", "data": new_data}
