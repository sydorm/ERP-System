from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import DictionaryItem, User
from app.schemas import DictionaryItemCreate, DictionaryItemUpdate, DictionaryItemResponse
from app.api.dependencies import get_current_active_user

router = APIRouter()

@router.get("/dictionaries/{category}", response_model=List[DictionaryItemResponse])
async def get_dictionary_items(
    category: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all active items for a specific category (e.g., 'UOM', 'ORDER_STATUS')
    """
    items = db.query(DictionaryItem).filter(
        DictionaryItem.company_id == current_user.company_id,
        DictionaryItem.category == category.upper(),
        DictionaryItem.is_active == True
    ).order_by(DictionaryItem.sort_order).all()
    
    return items

@router.post("/dictionaries", response_model=DictionaryItemResponse, status_code=status.HTTP_201_CREATED)
async def create_dictionary_item(
    item_in: DictionaryItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Add a new item to a dictionary
    """
    # Check for duplicates in this category
    existing = db.query(DictionaryItem).filter(
        DictionaryItem.company_id == current_user.company_id,
        DictionaryItem.category == item_in.category.upper(),
        DictionaryItem.code == item_in.code
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Item with this code already exists in category")

    item = DictionaryItem(
        **item_in.dict(),
        company_id=current_user.company_id
    )
    item.category = item.category.upper() # Ensure uppercase category
    
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.get("/dictionaries/meta/counts", response_model=dict)
def get_dictionary_counts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get count of items for each category
    """
    from sqlalchemy import func
    
    # This query groups by category and counts items
    results = db.query(
        DictionaryItem.category, 
        func.count(DictionaryItem.id)
    ).filter(
        DictionaryItem.company_id == current_user.company_id
    ).group_by(DictionaryItem.category).all()
    
    return {category: count for category, count in results}

@router.delete("/dictionaries/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dictionary_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a dictionary item (if not fixed)
    """
    item = db.query(DictionaryItem).filter(
        DictionaryItem.id == item_id,
        DictionaryItem.company_id == current_user.company_id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    if item.is_fixed:
        raise HTTPException(status_code=400, detail="Cannot delete system default items")
        
    db.delete(item)
    db.commit()
    return None
