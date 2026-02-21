from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import SalesInvoice, SalesInvoiceLine, SalesInvoiceStatus, User, RegisterType
from app.schemas.sales_invoice import SalesInvoiceCreate, SalesInvoiceUpdate, SalesInvoiceResponse
from app.api.dependencies import get_current_active_user
from app.services.posting_service import PostingService, PostingEntry
from app.services.sequence_service import SequenceService

router = APIRouter()

@router.get("/sales-invoices", response_model=List[SalesInvoiceResponse])
async def list_sales_invoices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List sales invoices for the current user's company.
    """
    return db.query(SalesInvoice).filter(SalesInvoice.company_id == current_user.company_id).all()

@router.post("/sales-invoices", response_model=SalesInvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_sales_invoice(
    invoice_data: SalesInvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new sales invoice and post stock movements (negative quantity).
    """
    # 0. Generate Number if empty or "Авто"
    invoice_num = invoice_data.invoice_number
    if not invoice_num or invoice_num.lower() in ["авто", "автоматично", "auto"]:
        invoice_num = SequenceService.get_next_number(db, "sales_invoice", "INV-")

    # 1. Create Invoice
    invoice = SalesInvoice(
        invoice_number=invoice_num,
        invoice_date=invoice_data.invoice_date,
        counterparty_id=invoice_data.counterparty_id,
        warehouse_id=invoice_data.warehouse_id,
        order_id=invoice_data.order_id,
        currency=invoice_data.currency,
        total_amount=invoice_data.total_amount,
        company_id=current_user.company_id,
        created_by=current_user.id,
        status=SalesInvoiceStatus.POSTED # Auto-post for now
    )
    db.add(invoice)
    db.flush()
    
    # 2. Add Lines
    for line_data in invoice_data.lines:
        line = SalesInvoiceLine(
            invoice_id=invoice.id,
            product_id=line_data.product_id,
            quantity=line_data.quantity,
            price=line_data.price,
            total=line_data.total
        )
        db.add(line)
    
    db.flush()
    
    # 3. Post Movements (Decrement Stock)
    entries = []
    for line_data in invoice_data.lines:
        entries.append(PostingEntry(
            register_type=RegisterType.STOCK,
            product_id=line_data.product_id,
            warehouse_id=invoice.warehouse_id,
            quantity=-float(line_data.quantity), # Negative for Sales
            amount=float(line_data.total),
            notes=f"Sales Invoice {invoice.invoice_number}"
        ))
        
        # Post AR/AP (Customer Debt)
        entries.append(PostingEntry(
            register_type=RegisterType.AR_AP,
            product_id=None,
            warehouse_id=None,
            quantity=0,
            amount=float(line_data.total), # Positive amount in AR_AP usually means they owe us
            notes=f"Sales Invoice {invoice.invoice_number}"
        ))
    
    PostingService.post_document(
        db, current_user.company_id, "SalesInvoice", invoice.id, entries
    )
    
    db.commit()
    db.refresh(invoice)
    return invoice

@router.get("/sales-invoices/{id}", response_model=SalesInvoiceResponse)
async def get_sales_invoice(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a single sales invoice.
    """
    invoice = db.query(SalesInvoice).filter(
        SalesInvoice.id == id,
        SalesInvoice.company_id == current_user.company_id
    ).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

@router.delete("/sales-invoices/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sales_invoice(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a sales invoice and unpost movements.
    """
    invoice = db.query(SalesInvoice).filter(
        SalesInvoice.id == id,
        SalesInvoice.company_id == current_user.company_id
    ).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Unpost before delete
    PostingService.unpost_document(db, current_user.company_id, "SalesInvoice", invoice.id)
    
    db.delete(invoice)
    db.commit()
    return None
