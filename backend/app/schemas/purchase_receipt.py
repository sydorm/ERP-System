from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from typing import List, Optional
from datetime import date
from uuid import UUID
from .purchase_receipt import PurchaseReceiptStatus

class PurchaseReceiptLineBase(BaseModel):
    product_id: UUID
    quantity: Decimal
    price: Decimal
    total: Decimal

class PurchaseReceiptLineCreate(PurchaseReceiptLineBase):
    pass

class PurchaseReceiptLineResponse(PurchaseReceiptLineBase):
    id: UUID
    
    model_config = ConfigDict(from_attributes=True)

class PurchaseReceiptBase(BaseModel):
    receipt_number: str
    receipt_date: date
    supplier_id: UUID
    warehouse_id: UUID
    currency: str = "UAH"
    total_amount: Decimal = Decimal("0.00")

class PurchaseReceiptCreate(PurchaseReceiptBase):
    lines: List[PurchaseReceiptLineCreate]

class PurchaseReceiptUpdate(BaseModel):
    receipt_number: Optional[str] = None
    receipt_date: Optional[date] = None
    supplier_id: Optional[UUID] = None
    warehouse_id: Optional[UUID] = None
    status: Optional[PurchaseReceiptStatus] = None
    lines: Optional[List[PurchaseReceiptLineCreate]] = None

class PurchaseReceiptResponse(PurchaseReceiptBase):
    id: UUID
    status: PurchaseReceiptStatus
    lines: List[PurchaseReceiptLineResponse]
    
    model_config = ConfigDict(from_attributes=True)
