"""
AI Routes - API endpoints for Kimi AI integration
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from ..services.kimi_service import kimi_service


router = APIRouter(prefix="/api/ai", tags=["AI Assistant"])


# Request/Response models
class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = None
    conversation_history: Optional[List[Dict[str, str]]] = None


class ChatResponse(BaseModel):
    response: str
    usage: Dict[str, int]


class ProductDescriptionRequest(BaseModel):
    product_name: str
    category: Optional[str] = None
    additional_info: Optional[str] = None


class ProductDescriptionResponse(BaseModel):
    description: str


class AnalyzeDataRequest(BaseModel):
    data_type: str
    data: Dict[str, Any]
    question: Optional[str] = None


class AnalyzeDataResponse(BaseModel):
    analysis: str


class StatusResponse(BaseModel):
    enabled: bool
    message: str


# Endpoints
@router.get("/status", response_model=StatusResponse)
async def get_ai_status():
    """
    Check if Kimi AI is enabled and configured
    """
    enabled = kimi_service.is_enabled()
    
    if enabled:
        return StatusResponse(
            enabled=True,
            message="Kimi AI готовий до роботи"
        )
    else:
        return StatusResponse(
            enabled=False,
            message="Kimi AI не налаштовано. Додайте KIMI_API_KEY в .env файл."
        )


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """
    Send a message to Kimi AI assistant
    
    **Example request:**
    ```json
    {
        "message": "Які товари найбільш продаються?",
        "context": "Користувач на сторінці Dashboard",
        "conversation_history": [
            {"role": "user", "content": "Привіт!"},
            {"role": "assistant", "content": "Вітаю! Чим можу допомогти?"}
        ]
    }
    ```
    """
    result = await kimi_service.chat(
        message=request.message,
        context=request.context,
        conversation_history=request.conversation_history
    )
    
    return ChatResponse(
        response=result["response"],
        usage=result["usage"]
    )


@router.post("/generate-description", response_model=ProductDescriptionResponse)
async def generate_product_description(request: ProductDescriptionRequest):
    """
    Generate product description using AI
    
    **Example request:**
    ```json
    {
        "product_name": "iPhone 15 Pro 256GB Black Titanium",
        "category": "Смартфони",
        "additional_info": "Флагманський смартфон з титановим корпусом"
    }
    ```
    """
    description = await kimi_service.generate_product_description(
        product_name=request.product_name,
        category=request.category,
        additional_info=request.additional_info
    )
    
    return ProductDescriptionResponse(description=description)


@router.post("/analyze-data", response_model=AnalyzeDataResponse)
async def analyze_business_data(request: AnalyzeDataRequest):
    """
    Analyze business data and get AI insights
    
    **Example request:**
    ```json
    {
        "data_type": "sales",
        "data": {
            "total_orders": 152,
            "total_revenue": 250000,
            "top_products": ["iPhone 15", "MacBook Pro", "AirPods"]
        },
        "question": "Як покращити продажі?"
    }
    ```
    """
    analysis = await kimi_service.analyze_business_data(
        data_type=request.data_type,
        data=request.data,
        question=request.question
    )
    
    return AnalyzeDataResponse(analysis=analysis)
