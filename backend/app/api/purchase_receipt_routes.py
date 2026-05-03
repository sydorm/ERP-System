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
        while True:
            receipt_num = SequenceService.get_next_number(db, "purchase_receipt", "PR-")
            existing = db.query(PurchaseReceipt).filter(PurchaseReceipt.receipt_number == receipt_num).first()
            if not existing:
                break

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
    from app.models.variant import ProductVariant, VariantValue
    from app.models.product import Product
    
    resolved_variants = {}
    
    for line_data in receipt_data.lines:
        resolved_variant_id = line_data.variant_id
        
        if not resolved_variant_id and line_data.attribute_values:
            vals = line_data.attribute_values
            
            def get_fp(v_list):
                parts = []
                for v in v_list:
                    a_id = str(v.get("attribute_id", ""))
                    key = str(v.get("option_id") or v.get("text_value") or "")
                    parts.append((a_id, key))
                return tuple(sorted(parts))
            
            incoming_fp = get_fp(vals)
            
            existing = db.query(ProductVariant).filter(
                ProductVariant.product_id == line_data.product_id,
                ProductVariant.is_active == True
            ).all()
            
            match_found = None
            for var in existing:
                var_vals = [{
                    "attribute_id": str(vv.attribute_id),
                    "option_id": str(vv.option_id) if vv.option_id else None,
                    "text_value": vv.text_value
                } for vv in var.values]
                if get_fp(var_vals) == incoming_fp:
                    match_found = var
                    break
            
            if match_found:
                resolved_variant_id = match_found.id
            else:
                product = db.query(Product).filter(Product.id == line_data.product_id).first()
                if product:
                    suffix_parts = []
                    for v in vals:
                        txt = v.get("text_value") or ""
                        if txt:
                            suffix_parts.append(txt.replace("×", "x").replace(" ", ""))
                    suffix = "-".join(suffix_parts) if suffix_parts else str(len(existing) + 1)
                    new_sku = f"{product.sku}-{suffix}"
                    
                    db_var = ProductVariant(
                        product_id=line_data.product_id,
                        sku=new_sku,
                        is_active=True,
                        is_primary=False
                    )
                    db.add(db_var)
                    db.flush()
                    
                    for v in vals:
                        db_vv = VariantValue(
                            variant_id=db_var.id,
                            attribute_id=UUID(v["attribute_id"]) if isinstance(v["attribute_id"], str) else v["attribute_id"],
                            option_id=UUID(v["option_id"]) if v.get("option_id") else None,
                            text_value=v.get("text_value")
                        )
                        db.add(db_vv)
                    db.flush()
                    resolved_variant_id = db_var.id
        
        resolved_variants[id(line_data)] = resolved_variant_id
        
        line = PurchaseReceiptLine(
            receipt_id=receipt.id,
            product_id=line_data.product_id,
            variant_id=resolved_variant_id,
            quantity=line_data.quantity,
            price=line_data.price,
            total=line_data.total,
            attribute_values=line_data.attribute_values,
            characteristic_width=line_data.characteristic_width,
            characteristic_height=line_data.characteristic_height
        )
        db.add(line)
    
    db.flush()
    
    # 3а. Update product cost prices BEFORE posting (so stock totals exclude current receipt)
    try:
        from app.services.cost_service import update_product_cost_from_receipt
        update_product_cost_from_receipt(
            db=db,
            company_id=current_user.company_id,
            receipt_id=receipt.id,
            receipt_number=receipt.receipt_number,
            receipt_date=receipt.receipt_date,
            supplier_id=receipt.supplier_id,
            lines=db.query(PurchaseReceiptLine).filter(PurchaseReceiptLine.receipt_id == receipt.id).all(),
            created_by_id=current_user.id,
        )
    except Exception as _cost_err:
        print(f"[cost_service] WARNING: failed to update cost prices: {_cost_err}")

    # 3. SOP: Register Movements (Posting Logic)
    entries = []
    for line_data in receipt_data.lines:
        entries.append(PostingEntry(
            register_type=RegisterType.STOCK,
            product_id=line_data.product_id,
            variant_id=resolved_variants.get(id(line_data)),
            warehouse_id=receipt.warehouse_id,
            quantity=float(line_data.quantity),
            amount=float(line_data.total),
            notes=f"Receipt {receipt.receipt_number}",
            attribute_values=line_data.attribute_values
        ))
    
    # 4. Financial: Accounts Payable (creditor liability to supplier)
    entries.append(PostingEntry(
        register_type=RegisterType.AR_AP,
        counterparty_id=receipt.supplier_id,
        amount=-float(receipt.total_amount),  # Negative = we owe money
        currency=receipt.currency or "UAH",
        notes=f"Закупівля {receipt.receipt_number}"
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

@router.put("/purchase-receipts/{id}", response_model=PurchaseReceiptResponse)
async def update_purchase_receipt(
    id: UUID,
    receipt_data: PurchaseReceiptUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    receipt = db.query(PurchaseReceipt).filter(
        PurchaseReceipt.id == id,
        PurchaseReceipt.company_id == current_user.company_id
    ).first()
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    
    # Simple update for now
    update_data = receipt_data.dict(exclude_unset=True, exclude={"lines"})
    for key, value in update_data.items():
        setattr(receipt, key, value)
    
    # Simple update - does not recalculate posting for now
    db.commit()
    db.refresh(receipt)
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
