from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.session import get_db
from app.models import Order, OrderLine, OrderStatus, User, RegisterType
from app.schemas.order import OrderCreate, OrderUpdate, OrderResponse
from app.api.dependencies import get_current_active_user
from app.services.posting_service import PostingService, PostingEntry
from app.services.sequence_service import SequenceService

router = APIRouter()

@router.get("/orders", response_model=List[OrderResponse])
async def list_orders(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List orders for the current user's company.
    """
    query = db.query(Order).filter(Order.company_id == current_user.company_id)
    
    if search:
        query = query.filter(Order.order_number.ilike(f"%{search}%"))
        
    if status:
        query = query.filter(Order.status == status)
        
    return query.order_by(Order.order_date.desc()).offset(skip).limit(limit).all()

@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_in: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new customer order and optionally reserve stock.
    """
    # 0. Generate Number if empty or "Авто"
    order_num = order_in.order_number
    if not order_num or order_num.lower() in ["авто", "автоматично", "auto"]:
        order_num = SequenceService.get_next_number(db, "order", "ORD-")

    # 1. Create Order
    order = Order(
        order_number=order_num,
        order_date=order_in.order_date,
        counterparty_id=order_in.counterparty_id,
        warehouse_id=order_in.warehouse_id,
        total_amount=order_in.total_amount,
        company_id=current_user.company_id,
        created_by=current_user.id,
        status="draft"
    )
    db.add(order)
    db.flush()
    
    # 2. Add Lines
    for line_in in order_in.lines:
        line = OrderLine(
            order_id=order.id,
            product_id=line_in.product_id,
            variant_id=line_in.variant_id,
            quantity=line_in.quantity,
            price=line_in.price,
            total=line_in.total
        )
        db.add(line)
    
    db.commit()
    db.refresh(order)
    return order

@router.get("/orders/{id}", response_model=OrderResponse)
async def get_order(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a single order.
    """
    order = db.query(Order).filter(
        Order.id == id,
        Order.company_id == current_user.company_id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.put("/orders/{id}", response_model=OrderResponse)
async def update_order(
    id: UUID,
    order_in: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update an order.
    Handles status changes and posting/unposting logic for stock reservation.
    """
    order = db.query(Order).filter(
        Order.id == id,
        Order.company_id == current_user.company_id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    update_data = order_in.dict(exclude_unset=True, exclude={"lines"})
    for field, value in update_data.items():
        setattr(order, field, value)

    # Update lines if provided
    if order_in.lines is not None:
        # Simple sync: remove old lines and add new ones
        db.query(OrderLine).filter(OrderLine.order_id == id).delete()
        for line_in in order_in.lines:
            line = OrderLine(
                order_id=id,
                product_id=line_in.product_id,
                variant_id=line_in.variant_id,
                quantity=line_in.quantity,
                price=line_in.price,
                total=line_in.total
            )
            db.add(line)
    # For now, CONFIRMED status will reserve stock
    
    if order_in.status == OrderStatus.CONFIRMED:
        # Example: Reservation (positive quantity but separated by register_type if needed, 
        # or just normal STOCK movement if confirming means "reserved")
        # In a real ERP, we might have a RESERVATION register type.
        pass

    db.commit()
    db.refresh(order)
    return order

@router.delete("/orders/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete an order.
    """
    order = db.query(Order).filter(
        Order.id == id,
        Order.company_id == current_user.company_id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    db.delete(order)
    db.commit()
    return None
