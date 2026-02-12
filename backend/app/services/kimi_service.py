"""
Kimi AI Service - Integration with Moonshot AI API
Provides AI assistant functionality for ERP system
"""
import os
from typing import Optional, List, Dict, Any
from openai import OpenAI
import httpx
from fastapi import HTTPException


class KimiService:
    """Service for interacting with Kimi AI (Moonshot AI)"""
    
    def __init__(self):
        self.api_key = os.getenv("KIMI_API_KEY", "")
        self.base_url = os.getenv("KIMI_API_BASE_URL", "https://api.moonshot.cn/v1")
        self.model = os.getenv("KIMI_MODEL", "moonshot-v1-8k")
        self.temperature = float(os.getenv("KIMI_TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("KIMI_MAX_TOKENS", "2000"))
        
        # Initialize OpenAI client with Kimi endpoints
        if self.api_key and self.api_key != "your-kimi-api-key-here":
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                http_client=httpx.Client(timeout=30.0)
            )
            self.enabled = True
        else:
            self.client = None
            self.enabled = False
    
    def is_enabled(self) -> bool:
        """Check if Kimi AI is properly configured"""
        return self.enabled
    
    async def chat(
        self, 
        message: str, 
        context: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Send a chat message to Kimi AI
        
        Args:
            message: User message
            context: Optional context about the current page/state
            conversation_history: Previous messages in the conversation
            
        Returns:
            Dict with 'response' and 'usage' information
        """
        if not self.is_enabled():
            raise HTTPException(
                status_code=503, 
                detail="Kimi AI не налаштовано. Додайте KIMI_API_KEY в .env файл."
            )
        
        try:
            # Build messages array
            messages = []
            
            # System message with context
            system_content = "Ти розумний AI асистент для ERP системи. Допомагай користувачам з аналізом даних, порадами щодо бізнесу, та відповідай українською мовою."
            if context:
                system_content += f"\n\nПоточний контекст: {context}"
            
            messages.append({
                "role": "system",
                "content": system_content
            })
            
            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history)
            
            # Add current message
            messages.append({
                "role": "user",
                "content": message
            })
            
            # Call Kimi API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            return {
                "response": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Помилка при зверненні до Kimi AI: {str(e)}"
            )
    
    async def generate_product_description(
        self, 
        product_name: str,
        category: Optional[str] = None,
        additional_info: Optional[str] = None
    ) -> str:
        """
        Generate product description using AI
        
        Args:
            product_name: Name of the product
            category: Product category
            additional_info: Any additional information
            
        Returns:
            Generated description
        """
        if not self.is_enabled():
            raise HTTPException(
                status_code=503,
                detail="Kimi AI не налаштовано"
            )
        
        try:
            prompt = f"Згенеруй професійний опис товару для інтернет-магазину.\n\n"
            prompt += f"Назва товару: {product_name}\n"
            
            if category:
                prompt += f"Категорія: {category}\n"
            
            if additional_info:
                prompt += f"Додаткова інформація: {additional_info}\n"
            
            prompt += "\nОпис має бути:\n"
            prompt += "- Професійним та привабливим\n"
            prompt += "- 2-4 речення\n"
            prompt += "- Підкреслювати ключові переваги\n"
            prompt += "- Українською мовою\n\n"
            prompt += "Створи лише опис товару, без додаткових коментарів."
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Ти експерт з написання товарних описів для інтернет-магазинів."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.8,  # More creative for descriptions
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Помилка генерації опису: {str(e)}"
            )
    
    async def analyze_business_data(
        self,
        data_type: str,
        data: Dict[str, Any],
        question: Optional[str] = None
    ) -> str:
        """
        Analyze business data and provide insights
        
        Args:
            data_type: Type of data (sales, inventory, etc.)
            data: The actual data to analyze
            question: Specific question about the data
            
        Returns:
            AI analysis and insights
        """
        if not self.is_enabled():
            raise HTTPException(
                status_code=503,
                detail="Kimi AI не налаштовано"
            )
        
        try:
            prompt = f"Проаналізуй наступні бізнес-дані:\n\n"
            prompt += f"Тип даних: {data_type}\n"
            prompt += f"Дані: {data}\n\n"
            
            if question:
                prompt += f"Питання: {question}\n\n"
            
            prompt += "Надай корисні інсайти та рекомендації українською мовою."
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Ти бізнес-аналітик, який допомагає керівникам приймати обґрунтовані рішення на основі даних."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Помилка аналізу даних: {str(e)}"
            )


# Singleton instance
kimi_service = KimiService()
