from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import sqlalchemy as sa
import uuid
from typing import List

from app.db.session import get_db
from app.api.dependencies import get_current_user
from app.models.production import ProductionOrder, ProductionOrderLine, ProductionOrderMaterial
from app.models.document_sequence import DocumentSequence
from app.schemas.production import ProductionOrderCreate, ProductionOrderUpdate, ProductionOrderResponse
from app.models.user import User
from app.services.posting_service import PostingService, PostingEntry
from app.models.register import RegisterType

router = APIRouter()

def get_next_production_order_number(db: Session, company_id: uuid.UUID) -> str:
    seq = db.query(DocumentSequence).filter(
        DocumentSequence.company_id == company_id,
        DocumentSequence.document_type == "production_order"
    ).with_for_update().first()
    
    if not seq:
        seq = DocumentSequence(
            company_id=company_id,
            document_type="production_order",
            prefix="PRD-",
            current_value=0
        )
        db.add(seq)
        
    seq.current_value += 1
    db.flush()
    return f"{seq.prefix}{seq.current_value:05d}"
    
@router.post("/", response_model=ProductionOrderResponse)
def create_production_order(
    order_in: ProductionOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # Generate number
        order_number = get_next_production_order_number(db, order_in.company_id)
        
        db_order = ProductionOrder(
            order_number=order_number,
            due_date=order_in.due_date,
            status=order_in.status,
            base_order_id=order_in.base_order_id,
            company_id=order_in.company_id,
            warehouse_id=order_in.warehouse_id,
            created_by=current_user.id,
            comment=order_in.comment
        )
        db.add(db_order)
        db.flush()
        
        for line_in in order_in.lines:
            db_line = ProductionOrderLine(
                production_order_id=db_order.id,
                product_id=line_in.product_id,
                variant_id=line_in.variant_id,
                specification_id=line_in.specification_id,
                quantity=line_in.quantity
            )
            db.add(db_line)
            
        for mat_in in order_in.materials:
            db_mat = ProductionOrderMaterial(
                production_order_id=db_order.id,
                component_id=mat_in.component_id,
                required_quantity=mat_in.required_quantity,
                unit_of_measure=mat_in.unit_of_measure,
                cost_estimate=mat_in.cost_estimate
            )
            db.add(db_mat)
            
        db.flush()
        
        # --- Handle Posting (Stock Movements) ---
        if db_order.status == "completed":
            entries = []
            for line in db_order.lines:
                entries.append(PostingEntry(
                    register_type=RegisterType.STOCK,
                    quantity=float(line.quantity),
                    product_id=line.product_id,
                    warehouse_id=db_order.warehouse_id,
                    notes=f"Production Output: {db_order.order_number}"
                ))
            for mat in db_order.materials:
                entries.append(PostingEntry(
                    register_type=RegisterType.STOCK,
                    quantity=-float(mat.required_quantity),
                    product_id=mat.component_id,
                    warehouse_id=db_order.warehouse_id,
                    notes=f"Production Usage: {db_order.order_number}"
                ))
            
            PostingService.post_document(
                db=db,
                company_id=db_order.company_id,
                document_type="production_order",
                document_id=db_order.id,
                entries=entries
            )
            db_order.completed_at = sa.func.now()

        db.commit()
        db.refresh(db_order)
        return db_order
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Database integrity error. Check references.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[ProductionOrderResponse])
def get_production_orders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    orders = db.query(ProductionOrder).order_by(ProductionOrder.created_at.desc()).offset(skip).limit(limit).all()
    return orders

@router.get("/{order_id}", response_model=ProductionOrderResponse)
def get_production_order(
    order_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = db.query(ProductionOrder).filter(ProductionOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Production order not found")
    return order
    
@router.put("/{order_id}", response_model=ProductionOrderResponse)
def update_production_order(
    order_id: uuid.UUID,
    order_in: ProductionOrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_order = db.query(ProductionOrder).filter(ProductionOrder.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Production order not found")
        
    try:
        update_data = order_in.model_dump(exclude_unset=True)
        lines_data = update_data.pop("lines", None)
        materials_data = update_data.pop("materials", None)
        
        for field, value in update_data.items():
            setattr(db_order, field, value)
            
        if lines_data is not None:
            # Simple overwrite
            db.query(ProductionOrderLine).filter(ProductionOrderLine.production_order_id == db_order.id).delete()
            for line_in in lines_data:
                db_line = ProductionOrderLine(
                    production_order_id=db_order.id,
                    product_id=line_in["product_id"],
                    variant_id=line_in.get("variant_id"),
                    specification_id=line_in.get("specification_id"),
                    quantity=line_in["quantity"]
                )
                db.add(db_line)
                
        if materials_data is not None:
            db.query(ProductionOrderMaterial).filter(ProductionOrderMaterial.production_order_id == db_order.id).delete()
            for mat_in in materials_data:
                db_mat = ProductionOrderMaterial(
                    production_order_id=db_order.id,
                    component_id=mat_in["component_id"],
                    required_quantity=mat_in["required_quantity"],
                    unit_of_measure=mat_in.get("unit_of_measure"),
                    cost_estimate=mat_in.get("cost_estimate")
                )
                db.add(db_mat)
        
        db.flush()
        
        # --- Handle Posting (Stock Movements) ---
        if db_order.status == "completed":
            entries = []
            # 1. Output (+)
            for line in db_order.lines:
                entries.append(PostingEntry(
                    register_type=RegisterType.STOCK,
                    quantity=float(line.quantity),
                    product_id=line.product_id,
                    warehouse_id=db_order.warehouse_id,
                    notes=f"Production Output: {db_order.order_number}"
                ))
            # 2. Consumption (-)
            for mat in db_order.materials:
                entries.append(PostingEntry(
                    register_type=RegisterType.STOCK,
                    quantity=-float(mat.required_quantity),
                    product_id=mat.component_id,
                    warehouse_id=db_order.warehouse_id,
                    notes=f"Production Usage: {db_order.order_number}"
                ))
            
            PostingService.post_document(
                db=db,
                company_id=db_order.company_id,
                document_type="production_order",
                document_id=db_order.id,
                entries=entries
            )
            
            if not db_order.completed_at:
                db_order.completed_at = sa.func.now()
        else:
            # If changed from completed back to something else, unpost
            PostingService.unpost_document(
                db=db,
                company_id=db_order.company_id,
                document_type="production_order",
                document_id=db_order.id
            )
            db_order.completed_at = None
                
        db.commit()
        db.refresh(db_order)
        return db_order
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Database integrity error.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{order_id}")
def delete_production_order(
    order_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_order = db.query(ProductionOrder).filter(ProductionOrder.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Production order not found")
        
    db.delete(db_order)
    db.commit()
    return {"ok": True}
