from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from datetime import datetime
from typing import Optional, List
from g.Моделювання.R1.backend.app.models.finance import TransactionType

class FinancialTransactionBase(BaseModel):
    bank_account_id: str
    order_id: Optional[str] = None
    transaction_type: TransactionType = TransactionType.IN
    amount: Decimal
    currency: str = "UAH"
    transaction_date: Optional[datetime] = None
    description: Optional[str] = None
    category: Optional[str] = None

class FinancialTransactionCreate(FinancialTransactionBase):
    pass

class FinancialTransaction(FinancialTransactionBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    company_id: str
    created_at: datetime
    updated_at: datetime

class FopIncomeAggregation(BaseModel):
    total: Decimal
    limit: Decimal
    percentage: float
    remaining: Decimal
    quarters: List[Decimal] # [Q1, Q2, Q3, Q4]
    by_account: List[dict] # { account_name: str, iban: str, amount: Decimal }

class TaxCalendarEvent(BaseModel):
    date: str
    title: str
    amount: Optional[str] = None
    type: str # 'payment', 'declaration'
