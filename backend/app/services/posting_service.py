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
