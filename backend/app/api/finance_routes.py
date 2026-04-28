from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, and_
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal

from app.db.session import get_db
from app.models.finance import FinancialTransaction, TransactionType
from app.models.company import Company, TaxGroup
from app.models.bank_account import BankAccount
from app.schemas.finance import FopIncomeAggregation, TaxCalendarEvent, FinancialTransactionCreate, FinancialTransaction as TransactionSchema
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/finance", tags=["Finance"])

@router.get("/fop-income", response_model=FopIncomeAggregation)
def get_fop_income(
    year: int = Query(default_factory=lambda: datetime.now().year),
    company_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Use default company if not provided
    if not company_id:
        company = db.query(Company).filter(Company.is_default == True).first()
        if not company:
            company = db.query(Company).first()
        if not company:
            raise HTTPException(status_code=404, detail="No company found")
        company_id = company.id
    else:
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

    # 1. Total income for the year
    total_income = db.query(func.sum(FinancialTransaction.amount)).filter(
        and_(
            FinancialTransaction.company_id == company_id,
            FinancialTransaction.transaction_type == TransactionType.IN,
            extract('year', FinancialTransaction.transaction_date) == year
        )
    ).scalar() or Decimal("0.00")

    # 2. Limit based on tax group or custom field
    # Standard limits for 2024-2026 (approximate, should be customizable)
    group_limits = {
        TaxGroup.GROUP_1: Decimal("1185700"),
        TaxGroup.GROUP_2: Decimal("5921400"),
        TaxGroup.GROUP_3: Decimal("8285700"),
    }
    
    limit = company.fop_income_limit or group_limits.get(company.tax_group, Decimal("5000000"))
    
    # 3. Quarterly breakdown
    quarters = []
    for q in range(1, 5):
        start_month = (q - 1) * 3 + 1
        end_month = q * 3
        q_income = db.query(func.sum(FinancialTransaction.amount)).filter(
            and_(
                FinancialTransaction.company_id == company_id,
                FinancialTransaction.transaction_type == TransactionType.IN,
                extract('year', FinancialTransaction.transaction_date) == year,
                extract('month', FinancialTransaction.transaction_date).between(start_month, end_month)
            )
        ).scalar() or Decimal("0.00")
        quarters.append(q_income)

    # 4. Breakdown by account
    accounts_data = []
    accounts = db.query(BankAccount).filter(BankAccount.company_id == company_id).all()
    for acc in accounts:
        acc_income = db.query(func.sum(FinancialTransaction.amount)).filter(
            and_(
                FinancialTransaction.bank_account_id == acc.id,
                FinancialTransaction.transaction_type == TransactionType.IN,
                extract('year', FinancialTransaction.transaction_date) == year
            )
        ).scalar() or Decimal("0.00")
        
        accounts_data.append({
            "account_name": acc.bank_name or acc.description or "Unknown Bank",
            "iban": acc.iban,
            "amount": acc_income
        })

    percentage = float((total_income / limit) * 100) if limit > 0 else 0
    remaining = limit - total_income

    return {
        "total": total_income,
        "limit": limit,
        "percentage": percentage,
        "remaining": remaining,
        "quarters": quarters,
        "by_account": accounts_data
    }

@router.get("/fop-calendar", response_model=List[TaxCalendarEvent])
def get_fop_calendar(
    company_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Use default company if not provided
    if not company_id:
        company = db.query(Company).filter(Company.is_default == True).first()
        if not company:
            company = db.query(Company).first()
        if not company:
            return []
    else:
        company = db.query(Company).filter(Company.id == company_id).first()

    # Standard reminders for Ukraine FOP (Simplified logic)
    events = []
    now = datetime.now()
    year = now.year
    month = now.month
    
    # ESV reminder (Example: 20th of every month)
    # Actually ESV is quarterly but many pay monthly
    esv_amount = company.tax_amount_esv or "1760"
    events.append({
        "date": f"{year}-{month:02d}-20",
        "title": "Сплатити ЄСВ",
        "amount": f"{esv_amount} грн",
        "type": "payment"
    })

    if company.tax_group == TaxGroup.GROUP_2:
        # Single Tax reminder (20th of every month)
        events.append({
            "date": f"{year}-{month:02d}-20",
            "title": "Сплатити Єдиний податок (Група 2)",
            "amount": company.tax_rate_single or "1500 грн",
            "type": "payment"
        })
    elif company.tax_group == TaxGroup.GROUP_3:
        # Quarterly Single Tax (5%)
        # Q1 due 40 days after quarter end
        q_end_dates = {1: "05-20", 2: "08-19", 3: "11-19", 4: "02-19"} # Approx
        q = (month - 1) // 3 + 1
        due_date = f"{year if q < 4 else year+1}-{q_end_dates[q]}"
        events.append({
            "date": due_date,
            "title": f"Сплатити Єдиний податок за Q{q}",
            "amount": "5% від доходу",
            "type": "payment"
        })

    # Declaration reminders
    if company.tax_group in [TaxGroup.GROUP_1, TaxGroup.GROUP_2]:
        # Annual declaration (usually Feb 9 or March 1 depending on year)
        events.append({
            "date": f"{year+1}-03-01",
            "title": "Подати річну декларацію",
            "amount": None,
            "type": "declaration"
        })
    else:
        # Quarterly declaration for Group 3
        q = (month - 1) // 3 + 1
        decl_dates = {1: "05-10", 2: "08-10", 3: "11-10", 4: "02-10"}
        due_date = f"{year if q < 4 else year+1}-{decl_dates[q]}"
        events.append({
            "date": due_date,
            "title": f"Подати декларацію за Q{q}",
            "amount": None,
            "type": "declaration"
        })

    return events

@router.post("/transactions", response_model=TransactionSchema)
def create_transaction(
    transaction: FinancialTransactionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Get company from current user or default
    company = db.query(Company).filter(Company.is_default == True).first()
    if not company:
        company = db.query(Company).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    db_transaction = FinancialTransaction(
        **transaction.model_dump(),
        company_id=company.id
    )
    db.add(db_transaction)
    
    # If transaction is linked to an order, potentially update order paid_amount
    if db_transaction.order_id and db_transaction.transaction_type == TransactionType.IN:
        from app.models.order import Order
        order = db.query(Order).filter(Order.id == db_transaction.order_id).first()
        if order:
            order.paid_amount = (order.paid_amount or 0) + db_transaction.amount
            # Update status if fully paid
            if order.paid_amount >= order.total_amount:
                order.payment_status = "paid"
            elif order.paid_amount > 0:
                order.payment_status = "partially_paid"

    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@router.delete("/transactions/{transaction_id}")
def delete_transaction(
    transaction_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    transaction = db.query(FinancialTransaction).filter(FinancialTransaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    order_id = transaction.order_id
    
    db.delete(transaction)
    db.commit()
    
    # Recalculate order paid amount if it was an income transaction
    if order_id:
        from app.models.order import Order
        order = db.query(Order).filter(Order.id == order_id).first()
        if order:
            total_paid = db.query(func.sum(FinancialTransaction.amount)).filter(
                FinancialTransaction.order_id == order_id,
                FinancialTransaction.transaction_type == TransactionType.IN
            ).scalar() or 0
            
            order.paid_amount = total_paid
            
            if order.paid_amount >= order.total_amount:
                order.payment_status = "paid"
            elif order.paid_amount > 0:
                order.payment_status = "partially_paid"
            else:
                order.payment_status = "unpaid"
            
            db.commit()
            
    return {"ok": True}
