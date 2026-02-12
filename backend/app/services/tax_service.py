from datetime import datetime
from typing import Dict, Any

class TaxService:
    """
    Mock service to simulate fetching official tax rates from Ukrainian registries (DPS).
    In a real scenario, this would call an API or scrape official data.
    """
    
    @staticmethod
    def get_current_rates() -> Dict[str, Any]:
        """
        Returns recent tax rates for 2025 (Ukraine).
        """
        return {
            "tax_amount_esv": "1760.00", # 22% of min salary (8000 * 0.22)
            "tax_rate_single_3": "5%",    # 3rd group
            "military_tax_rate": "5%",    # Recently increased to 5% in late 2024/2025
            "min_salary": "8000",
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source": "Офіційні дані ДПС (Симуляція)"
        }

tax_service = TaxService()
