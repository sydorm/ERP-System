from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal

class TaxSettings(BaseModel):
    tax_year: int = 2026
    min_wage: Decimal = Decimal("8647.00")
    subsistence_min: Decimal = Decimal("3328.00")
    tax_group: str = "GROUP_2"
    is_vat_payer: bool = False
    
    # Rates and Multipliers
    esv_rate: Decimal = Decimal("0.22")
    single_tax_rate: Decimal = Decimal("0.20")
    military_levy_rate: Decimal = Decimal("0.10") # For Fixed (G1, G2, G4)
    military_levy_rate_percent: Decimal = Decimal("0.01") # For Turnover (G3)
    
    limit_multiplier_g1: int = 167
    limit_multiplier_g2: int = 834
    limit_multiplier_g3: int = 1167
    
    last_updated: Optional[datetime] = None

class TaxSettingsUpdate(BaseModel):
    settings: Dict[str, Any]
