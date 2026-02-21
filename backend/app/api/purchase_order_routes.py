from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.purchase_order import PurchaseOrder, PurchaseOrderLine, PurchaseOrderStatus
from app.models.user import User
from app.schemas.purchase_order import PurchaseOrderCreate, PurchaseOrderUpdate, PurchaseOrderResponse
from app.api.dependencies import get_current_active_user
from app.services.sequence_service import SequenceService

router = APIRouter()

@router.get("/purchase-orders", response_model=List[PurchaseOrderResponse])
async def list_purchase_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return db.query(PurchaseOrder).filter(PurchaseOrder.company_id == current_user.company_id).all()

@router.post("/purchase-orders", response_model=PurchaseOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase_order(
    order_data: PurchaseOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # 0. Generate Number if empty or "Авто"
    order_num = order_data.order_number
    if not order_num or order_num.lower() in ["авто", "автоматично", "auto"]:
        order_num = SequenceService.get_next_number(db, "purchase_order", "PO-")

    # 1. Create Order
    order = PurchaseOrder(
        order_number=order_num,
        order_date=order_data.order_date,
        expected_date=order_data.expected_date,
        supplier_id=order_data.supplier_id,
        warehouse_id=order_data.warehouse_id,
        currency=order_data.currency,
        total_amount=order_data.total_amount,
        company_id=current_user.company_id,
        created_by=current_user.id,
        notes=order_data.notes,
        status=PurchaseOrderStatus(order_data.status) if order_data.status else PurchaseOrderStatus.DRAFT
    )
    db.add(order)
    db.flush()
    
    # 2. Add Lines
    for line_data in order_data.lines:
        line = PurchaseOrderLine(
            order_id=order.id,
            product_id=line_data.product_id,
            variant_id=line_data.variant_id,
            quantity=line_data.quantity,
            price=line_data.price,
            total=line_data.total
        )
        db.add(line)
    
    db.commit()
    db.refresh(order)
    return order

@router.get("/purchase-orders/{id}", response_model=PurchaseOrderResponse)
async def get_purchase_order(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    order = db.query(PurchaseOrder).filter(
        PurchaseOrder.id == id,
        PurchaseOrder.company_id == current_user.company_id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Purchase Order not found")
    return order

@router.put("/purchase-orders/{id}", response_model=PurchaseOrderResponse)
async def update_purchase_order(
    id: UUID,
    order_data: PurchaseOrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    order = db.query(PurchaseOrder).filter(
        PurchaseOrder.id == id,
        PurchaseOrder.company_id == current_user.company_id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Purchase Order not found")
        
    update_data = order_data.dict(exclude_unset=True, exclude={"lines"})
    for key, value in update_data.items():
        if key == "status":
            setattr(order, key, PurchaseOrderStatus(value))
        else:
            setattr(order, key, value)
            
    if order_data.lines is not None:
        db.query(PurchaseOrderLine).filter(PurchaseOrderLine.order_id == id).delete()
        for line_data in order_data.lines:
            line = PurchaseOrderLine(
                order_id=order.id,
                product_id=line_data.product_id,
                variant_id=line_data.variant_id,
                quantity=line_data.quantity,
                price=line_data.price,
                total=line_data.total
            )
            db.add(line)
            
    db.commit()
    db.refresh(order)
    return order

@router.delete("/purchase-orders/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_purchase_order(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    order = db.query(PurchaseOrder).filter(
        PurchaseOrder.id == id,
        PurchaseOrder.company_id == current_user.company_id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Purchase Order not found")
    
    db.delete(order)
    db.commit()
    return None
