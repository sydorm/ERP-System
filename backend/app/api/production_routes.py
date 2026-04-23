from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
import sqlalchemy as sa
import uuid
from typing import List
from decimal import Decimal

from app.db.session import get_db
from app.api.dependencies import get_current_user
from app.models.production import ProductionOrder, ProductionOrderLine, ProductionOrderMaterial, ProductionOrderWorkerAssignment
from app.models.hr import Employee, EmployeeRole, PayrollTransaction
from app.models.document_sequence import DocumentSequence
from app.schemas.production import ProductionOrderCreate, ProductionOrderUpdate, ProductionOrderResponse
from app.models.user import User
from app.models.dictionary import DictionaryItem
from app.services.posting_service import PostingService, PostingEntry
from app.models.register import RegisterType

router = APIRouter()

def get_next_production_order_number(db: Session, company_id: uuid.UUID) -> str:
    # Note: DocumentSequence currently doesn't have company_id, so it's global per document_type
    seq = db.query(DocumentSequence).filter(
        DocumentSequence.document_type == "production_order"
    ).with_for_update().first()
    
    if not seq:
        seq = DocumentSequence(
            document_type="production_order",
            prefix="PRD-",
            next_number=1,
            padding=5
        )
        db.add(seq)
        db.flush()
        
    num = seq.next_number
    seq.next_number += 1
    db.flush()
    return f"{seq.prefix}{num:0{seq.padding}d}"
    
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
            comment=order_in.comment,
            source_type=order_in.source_type,
            source_id=order_in.source_id,
            client_id=order_in.client_id,
            priority=order_in.priority
        )
        db.add(db_order)
        db.flush()
        
        # Save Worker Assignments
        if order_in.assignments:
            for assign_in in order_in.assignments:
                db_assign = ProductionOrderWorkerAssignment(
                    production_order_id=db_order.id,
                    employee_id=assign_in.employee_id,
                    stage_id=assign_in.stage_id,
                    brigade_id=assign_in.brigade_id,
                    quantity=assign_in.quantity,
                    planned_hours=assign_in.planned_hours,
                    status=assign_in.status
                )
                db.add(db_assign)
                
        for line_in in order_in.lines:
            db_line = ProductionOrderLine(
                production_order_id=db_order.id,
                product_id=line_in.product_id,
                variant_id=line_in.variant_id,
                specification_id=line_in.specification_id,
                quantity=line_in.quantity
            )
            db.add(db_line)
            
            # --- AUTO-CALCULATE MATERIALS ---
            # If materials list is empty, try to explode the specification
            if not order_in.materials and line_in.specification_id:
                from app.models.specification import ProductSpecification, SpecificationItem, ProductSpecificationStage
                from app.models.product import Product
                from app.services.specification_service import SpecificationService
                from sqlalchemy.orm import joinedload
                
                # Get the product to get dimensions
                product = db.query(Product).filter(Product.id == line_in.product_id).first()
                if not product:
                    continue
                
                # Get the specification
                spec = db.query(ProductSpecification).options(
                    joinedload(ProductSpecification.items).joinedload(SpecificationItem.component),
                    joinedload(ProductSpecification.stages).joinedload(ProductSpecificationStage.stage)
                ).filter(ProductSpecification.id == line_in.specification_id).first()
                
                if spec:
                    custom_attrs = {}
                    if line_in.variant_id:
                        from app.models.variant import ProductVariant, VariantValue
                        variant = db.query(ProductVariant).options(
                            joinedload(ProductVariant.values).joinedload(VariantValue.attribute),
                            joinedload(ProductVariant.values).joinedload(VariantValue.option)
                        ).filter(ProductVariant.id == line_in.variant_id).first()
                        
                        if variant:
                            for val in variant.values:
                                attr_name = val.attribute.name if val.attribute else None
                                if not attr_name: continue
                                try:
                                    if val.option and val.option.value:
                                        custom_attrs[attr_name] = float(val.option.value)
                                    elif val.text_value:
                                        custom_attrs[attr_name] = float(val.text_value)
                                except ValueError:
                                    pass

                    parent_dims = {
                        'width_cm': float(product.width_cm or 0),
                        'height_cm': float(product.height_cm or 0),
                        'length_cm': float(product.length_cm or 0),
                        'weight_kg': float(product.weight_kg or 0),
                        'custom_attributes': custom_attrs
                    }
                    
                    for spec_item in spec.items:
                        calc_qty = SpecificationService.calculate_item_quantity(spec_item, parent_dims)
                        # Multiply by the quantity of the produced product
                        total_qty = calc_qty * Decimal(str(line_in.quantity))
                        
                        db_mat = ProductionOrderMaterial(
                            production_order_id=db_order.id,
                            component_id=spec_item.component_id,
                            required_quantity=total_qty,
                            unit_of_measure=spec_item.unit_of_measure or (spec_item.component.unit_of_measure if spec_item.component else "шт"),
                            cost_estimate=0 # Will be updated later if needed
                        )
                        db.add(db_mat)
                        
                    # --- AUTO-POPULATE STAGES ---
                    # If assignments were not provided, get them from specification
                    if not order_in.assignments and spec.stages:
                        for spec_stage in spec.stages:
                            db_assign = ProductionOrderWorkerAssignment(
                                production_order_id=db_order.id,
                                stage_id=spec_stage.stage_id,
                                brigade_id=spec_stage.brigade_id,
                                quantity=line_in.quantity,
                                planned_hours=spec_stage.duration_hours * Decimal(str(line_in.quantity)),
                                status="pending"
                            )
                            db.add(db_assign)
            
        # If materials were provided manually, use them
        if order_in.materials:
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
    orders = db.query(ProductionOrder).options(
        joinedload(ProductionOrder.assignments).joinedload(ProductionOrderWorkerAssignment.stage)
    ).order_by(ProductionOrder.created_at.desc()).offset(skip).limit(limit).all()
    return orders

@router.get("/{order_id}", response_model=ProductionOrderResponse)
def get_production_order(
    order_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = db.query(ProductionOrder).options(
        joinedload(ProductionOrder.assignments).joinedload(ProductionOrderWorkerAssignment.stage),
        joinedload(ProductionOrder.lines),
        joinedload(ProductionOrder.materials)
    ).filter(ProductionOrder.id == order_id).first()
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
    db_order = db.query(ProductionOrder).options(
        joinedload(ProductionOrder.assignments).joinedload(ProductionOrderWorkerAssignment.stage),
        joinedload(ProductionOrder.lines),
        joinedload(ProductionOrder.materials)
    ).filter(ProductionOrder.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Production order not found")
        
    try:
        update_data = order_in.model_dump(exclude_unset=True)
        lines_data = update_data.pop("lines", None)
        materials_data = update_data.pop("materials", None)
        assignments_data = update_data.pop("assignments", None)
        
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

        if assignments_data is not None:
            db.query(ProductionOrderWorkerAssignment).filter(ProductionOrderWorkerAssignment.production_order_id == db_order.id).delete()
            for assign_in in assignments_data:
                db_assign = ProductionOrderWorkerAssignment(
                    production_order_id=db_order.id,
                    employee_id=assign_in.get("employee_id"),
                    stage_id=assign_in.get("stage_id"),
                    brigade_id=assign_in.get("brigade_id"),
                    quantity=assign_in.get("quantity"),
                    planned_hours=assign_in.get("planned_hours", 0.0),
                    status=assign_in.get("status", "pending")
                )
                db.add(db_assign)

        db.flush()
        
        # --- Handle Automated Payroll Accruals (Personnel v3) ---
        if db_order.status == "completed":
            # 1. Get accrual type dictionary item (Category: ACCRUAL_TYPE, Code: PRODUCTION)
            # Fallback if not found: use any accrual category linked to the employee role
            for assign in db_order.assignments:
                # Find employee rate for this specific stage
                role = db.query(EmployeeRole).filter(
                    EmployeeRole.employee_id == assign.employee_id,
                    EmployeeRole.role_id == assign.stage_id,
                    EmployeeRole.is_active == True
                ).first()
                
                if role:
                    # Calculate quantity (order quantity if not specified on assignment)
                    # For simplicity, we use total quantity of first line if assignment quantity is null
                    calc_qty = assign.quantity or (db_order.lines[0].quantity if db_order.lines else 1)
                    total_amount = role.rate * Decimal(str(calc_qty))
                    
                    # Create Payroll Transaction
                    new_accrual = PayrollTransaction(
                        employee_id=assign.employee_id,
                        amount=total_amount,
                        transaction_type='ACCRUAL',
                        date=sa.func.current_date(),
                        category_id=role.accrual_type_id,
                        production_order_id=db_order.id,
                        created_by=current_user.id,
                        description=f"Автоматичне нарахування: {db_order.order_number} (Етап: {assign.stage.name if assign.stage else '?'})"
                    )
                    db.add(new_accrual)

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
