from typing import List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.session import get_db
from app.models import Product, Counterparty, Warehouse, User
from app.api.dependencies import get_current_active_user

router = APIRouter()

def _get_model_and_name(item_type: str):
    if item_type == "product":
        return Product, "Товар"
    elif item_type == "counterparty":
        return Counterparty, "Контрагент"
    elif item_type == "warehouse":
        return Warehouse, "Склад"
    else:
        raise HTTPException(status_code=400, detail="Unknown item type")


@router.get("/trash", response_model=Dict[str, List[Dict[str, Any]]])
async def get_trash_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all softly deleted items for the company, grouped by type.
    Must be an admin to access (in a real app you'd enforce roles, assuming all active users here or check role).
    """
    # Here you might want to check current_user.role == 'admin' based on your implementation
    
    products = db.query(Product).filter(
        Product.company_id == current_user.company_id,
        Product.is_deleted == True
    ).all()
    
    counterparties = db.query(Counterparty).filter(
        Counterparty.company_id == current_user.company_id,
        Counterparty.is_deleted == True
    ).all()
    
    warehouses = db.query(Warehouse).filter(
        Warehouse.company_id == current_user.company_id,
        Warehouse.is_deleted == True
    ).all()
    
    return {
        "products": [{"id": str(p.id), "name": p.name, "type": "product", "sku": p.sku} for p in products],
        "counterparties": [{"id": str(c.id), "name": c.name, "type": "counterparty", "tax_id": c.tax_id} for c in counterparties],
        "warehouses": [{"id": str(w.id), "name": w.name, "type": "warehouse"} for w in warehouses]
    }


@router.post("/trash/restore/{item_type}/{item_id}")
async def restore_trash_item(
    item_type: str,
    item_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Restore a softly deleted item.
    """
    ModelClass, _ = _get_model_and_name(item_type)
    
    item = db.query(ModelClass).filter(
        ModelClass.id == item_id,
        ModelClass.company_id == current_user.company_id,
        ModelClass.is_deleted == True
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found in trash")
        
    item.is_deleted = False
    db.commit()
    return {"status": "success", "message": "Item restored"}


@router.delete("/trash/hard_delete/{item_type}/{item_id}")
async def hard_delete_trash_item(
    item_type: str,
    item_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Permanently delete an item from the database.
    """
    ModelClass, item_name = _get_model_and_name(item_type)
    
    item = db.query(ModelClass).filter(
        ModelClass.id == item_id,
        ModelClass.company_id == current_user.company_id,
        ModelClass.is_deleted == True
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found in trash")
        
    try:
        db.delete(item)
        db.commit()
        return {"status": "success", "message": f"{item_name} permanently deleted"}
    except Exception as e:
        db.rollback()
        # This catches foreign key constraint violations if they somehow bypassed the check
        raise HTTPException(
            status_code=400, 
            detail="Помилка при фізичному видаленні. Можливо, на об'єкт існують приховані посилання у базі даних."
        )
