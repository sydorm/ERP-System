from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.db.session import get_db
from app.models import PurchaseReceipt, PurchaseReceiptLine, PurchaseReceiptStatus, User
from app.schemas.purchase_receipt import PurchaseReceiptCreate, PurchaseReceiptUpdate, PurchaseReceiptResponse
from app.api.dependencies import get_current_active_user
from app.services.posting_service import PostingService, PostingEntry, RegisterType
from app.services.sequence_service import SequenceService

router = APIRouter()

@router.get("/purchase-receipts", response_model=List[PurchaseReceiptResponse])
async def list_purchase_receipts(
    supplier_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(PurchaseReceipt).filter(PurchaseReceipt.company_id == current_user.company_id)
    if supplier_id:
        query = query.filter(PurchaseReceipt.supplier_id == supplier_id)
    return query.all()

@router.post("/purchase-receipts", response_model=PurchaseReceiptResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase_receipt(
    receipt_data: PurchaseReceiptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # 0. Generate Number if empty or "Авто"
    receipt_num = receipt_data.receipt_number
    if not receipt_num or receipt_num.lower() in ["авто", "автоматично", "auto"]:
        receipt_num = SequenceService.get_next_number(db, "purchase_receipt", "PR-")

    # 1. Create Receipt
    receipt = PurchaseReceipt(
        receipt_number=receipt_num,
        receipt_date=receipt_data.receipt_date,
        supplier_id=receipt_data.supplier_id,
        warehouse_id=receipt_data.warehouse_id,
        currency=receipt_data.currency,
        total_amount=receipt_data.total_amount,
        base_order_id=receipt_data.base_order_id,
        company_id=current_user.company_id,
        created_by=current_user.id,
        status=PurchaseReceiptStatus.POSTED # Auto-post for now in simplified flow
    )
    db.add(receipt)
    db.flush()
    
    # 1a. Update Parent Order Status if exists
    if receipt_data.base_order_id:
        from app.models.purchase_order import PurchaseOrder, PurchaseOrderStatus
        db.query(PurchaseOrder).filter(
            PurchaseOrder.id == receipt_data.base_order_id
        ).update({"status": PurchaseOrderStatus.DONE})
    
    # 2. Add Lines
    for line_data in receipt_data.lines:
        line = PurchaseReceiptLine(
            receipt_id=receipt.id,
            product_id=line_data.product_id,
            variant_id=line_data.variant_id,
            quantity=line_data.quantity,
            price=line_data.price,
            total=line_data.total,
            attribute_values=line_data.attribute_values
        )
        db.add(line)
    
    db.flush()
    
    # 3. SOP: Register Movements (Posting Logic)
    entries = []
    for line_data in receipt_data.lines:
        entries.append(PostingEntry(
            register_type=RegisterType.STOCK,
            product_id=line_data.product_id,
            variant_id=line_data.variant_id,
            warehouse_id=receipt.warehouse_id,
            quantity=float(line_data.quantity),
            amount=float(line_data.total),
            notes=f"Receipt {receipt.receipt_number}",
            attribute_values=line_data.attribute_values
        ))
    
    PostingService.post_document(
        db, current_user.company_id, "PurchaseReceipt", receipt.id, entries
    )
    
    db.commit()
    db.refresh(receipt)
    return receipt

@router.get("/purchase-receipts/{id}", response_model=PurchaseReceiptResponse)
async def get_purchase_receipt(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    receipt = db.query(PurchaseReceipt).options(
        joinedload(PurchaseReceipt.lines)
    ).filter(
        PurchaseReceipt.id == id,
        PurchaseReceipt.company_id == current_user.company_id
    ).first()
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return receipt

@router.delete("/purchase-receipts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_purchase_receipt(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    receipt = db.query(PurchaseReceipt).filter(
        PurchaseReceipt.id == id,
        PurchaseReceipt.company_id == current_user.company_id
    ).first()
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    
    # SOP: Unpost before delete
    PostingService.unpost_document(db, current_user.company_id, "PurchaseReceipt", receipt.id)
    
    db.delete(receipt)
    db.commit()
    return None
