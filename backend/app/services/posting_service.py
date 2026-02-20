from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.models import AccumulationRegister, RegisterType

class PostingEntry:
    """Helper class to define a single register entry"""
    def __init__(
        self,
        register_type: RegisterType,
        quantity: float = 0,
        amount: float = 0,
        product_id: Optional[UUID] = None,
        warehouse_id: Optional[UUID] = None,
        counterparty_id: Optional[UUID] = None,
        bank_account_id: Optional[UUID] = None,
        currency: str = "UAH",
        notes: Optional[str] = None
    ):
        self.register_type = register_type
        self.quantity = quantity
        self.amount = amount
        self.product_id = product_id
        self.warehouse_id = warehouse_id
        self.counterparty_id = counterparty_id
        self.bank_account_id = bank_account_id
        self.currency = currency
        self.notes = notes

class PostingService:
    @staticmethod
    def post_document(
        db: Session,
        company_id: UUID,
        document_type: str,
        document_id: UUID,
        entries: List[PostingEntry]
    ):
        """
        Create register records for a document.
        Automatically removes previous records for this document to ensure idempotency.
        """
        # 1. Unpost first (idempotency)
        PostingService.unpost_document(db, company_id, document_type, document_id)
        
        # 2. Add new entries
        for entry in entries:
            db_record = AccumulationRegister(
                company_id=company_id,
                register_type=entry.register_type,
                product_id=entry.product_id,
                warehouse_id=entry.warehouse_id,
                counterparty_id=entry.counterparty_id,
                bank_account_id=entry.bank_account_id,
                quantity=entry.quantity,
                amount=entry.amount,
                currency=entry.currency,
                document_type=document_type,
                document_id=document_id,
                notes=entry.notes
            )
            db.add(db_record)
        
        db.flush()

    @staticmethod
    def unpost_document(
        db: Session,
        company_id: UUID,
        document_type: str,
        document_id: UUID
    ):
        """Remove all register records associated with a document"""
        db.query(AccumulationRegister).filter(
            AccumulationRegister.company_id == company_id,
            AccumulationRegister.document_type == document_type,
            AccumulationRegister.document_id == document_id
        ).delete()
        db.flush()

    @staticmethod
    def get_stock_balances(db: Session, company_id: UUID, product_ids: Optional[List[UUID]] = None):
        """
        Get current stock balances for products.
        Returns a dictionary mapping product_id to current quantity.
        """
        from sqlalchemy import func
        query = db.query(
            AccumulationRegister.product_id,
            func.sum(AccumulationRegister.quantity).label("balance")
        ).filter(
            AccumulationRegister.company_id == company_id,
            AccumulationRegister.register_type == RegisterType.STOCK
        )

        if product_ids:
            query = query.filter(AccumulationRegister.product_id.in_(product_ids))

        results = query.group_by(AccumulationRegister.product_id).all()
        return {str(r.product_id): float(r.balance or 0) for r in results if r.product_id}

    @staticmethod
    def get_overall_statistics(db: Session, company_id: UUID):
        """
        Get overall stock statistics for the company.
        """
        from app.models import Product
        from sqlalchemy import func

        # 1. Total active products
        total_products = db.query(func.count(Product.id)).filter(
            Product.company_id == company_id,
            Product.is_active == True
        ).scalar() or 0

        # 2. Balances for all products
        balances = PostingService.get_stock_balances(db, company_id)
        
        in_stock_count = 0
        low_stock_count = 0
        out_of_stock_count = 0
        
        # We need to consider all active products, even those without register entries (0 balance)
        all_active_product_ids = [str(id[0]) for id in db.query(Product.id).filter(
            Product.company_id == company_id,
            Product.is_active == True
        ).all()]

        for p_id in all_active_product_ids:
            qty = balances.get(p_id, 0)
            if qty > 5: # Threshold for "in stock"
                in_stock_count += 1
            elif 0 < qty <= 5: # Threshold for "low stock"
                low_stock_count += 1
            else:
                out_of_stock_count += 1

        return {
            "total_products": total_products,
            "in_stock": in_stock_count,
            "low_stock": low_stock_count,
            "out_of_stock": out_of_stock_count
        }
