import httpx
import json
import logging
from typing import Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class AnthropicService:
    """
    Service for interacting with Anthropic (Claude) API
    """
    
    def __init__(self):
        self.api_key = getattr(settings, "ANTHROPIC_API_KEY", None)
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.model = "claude-3-5-sonnet-20240620"
        
    def is_enabled(self) -> bool:
        return bool(self.api_key)

    async def get_tax_rates(self, tax_group: str, year: int = 2026) -> Dict[str, Any]:
        """
        Query Claude for actual tax rates for a specific group and year.
        Returns a JSON object with keys: min_wage, subsistence_min, limits, monthly.
        """
        if not self.is_enabled():
            # Return hardcoded 2026 data if API key is missing (fallback/mock)
            logger.warning("ANTHROPIC_API_KEY not found. Returning fallback data for 2026.")
            return self._get_fallback_data(tax_group, year)

        prompt = f"""
        Які актуальні ставки податків для ФОП {tax_group} в Україні на {year} рік? 
        Мені потрібні: Мінімальна зарплата (МЗП), Прожитковий мінімум (ПМ), 
        ліміти доходу для всіх груп, та щомісячні платежі (ЄСВ, Єдиний податок, Військовий збір).
        
        Відповідь надай ТІЛЬКИ у форматі JSON за такою структурою:
        {{
            "year": {year},
            "min_wage": 8647,
            "subsistence_min": 3328,
            "limits": {{
                "group_1": 1444049,
                "group_2": 7211598,
                "group_3": 10091049
            }},
            "monthly": {{
                "esv": 1902.34,
                "single_tax": 1729.40,
                "military_levy": 864.70
            }}
        }}
        """

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        data = {
            "model": self.model,
            "max_tokens": 1000,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.api_url, headers=headers, json=data)
                response.raise_for_status()
                result = response.json()
                
                content = result["content"][0]["text"]
                # Extract JSON from response (handling possible markdown)
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                
                return json.loads(content.strip())
        except Exception as e:
            logger.error(f"Error calling Anthropic API: {str(e)}")
            return self._get_fallback_data(tax_group, year)

    def _get_fallback_data(self, tax_group: str, year: int) -> Dict[str, Any]:
        """Hardcoded data for 2026 based on user TZ"""
        return {
            "year": 2026,
            "min_wage": 8647,
            "subsistence_min": 3328,
            "limits": {
                "group_1": 1444049, # 167 * 8647
                "group_2": 7211598, # 834 * 8647
                "group_3": 10091049 # 1167 * 8647
            },
            "monthly": {
                "esv": 1902.34,
                "single_tax": 1729.40 if tax_group == "GROUP_2" else 0,
                "military_levy": 864.70
            }
        }

anthropic_service = AnthropicService()
