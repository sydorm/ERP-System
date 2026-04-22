from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import DictionaryItem, User
from app.schemas import DictionaryItemCreate, DictionaryItemUpdate, DictionaryItemResponse
from app.api.dependencies import get_current_active_user

router = APIRouter()

@router.get("/dictionaries/items", response_model=List[DictionaryItemResponse])
async def get_dictionary_items_by_type(
    type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generic endpoint to get dictionary items by type query parameter.
    Matches frontend pattern: /api/v1/dictionaries/items?type=CATEGORY
    """
    return await get_dictionary_items(category=type, db=db, current_user=current_user)

@router.get("/dictionaries/{category}", response_model=List[DictionaryItemResponse])
async def get_dictionary_items(
    category: str,
    all_items: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get items for a specific category (e.g., 'UOM', 'LEAD_SOURCE')
    By default returns only active items, sorted by 'order'
    """
    query = db.query(DictionaryItem).filter(
        DictionaryItem.company_id == current_user.company_id,
        (DictionaryItem.category == category.upper()) | (DictionaryItem.type == category.lower())
    )
    
    if not all_items:
        query = query.filter(DictionaryItem.is_active == True)
        
    return query.order_by(DictionaryItem.order, DictionaryItem.sort_order).all()

@router.get("/dictionaries/{category}/all", response_model=List[DictionaryItemResponse])
async def get_all_dictionary_items(
    category: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all items (active and inactive) for a specific category (for administration)
    """
    return await get_dictionary_items(category, all_items=True, db=db, current_user=current_user)


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

@router.put("/dictionaries/{item_id}", response_model=DictionaryItemResponse)
async def update_dictionary_item(
    item_id: str,
    item_in: DictionaryItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a dictionary item
    """
    item = db.query(DictionaryItem).filter(
        DictionaryItem.id == item_id,
        DictionaryItem.company_id == current_user.company_id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    # Check for duplicate code if code changed
    if item_in.code and item_in.code != item.code:
        existing = db.query(DictionaryItem).filter(
            DictionaryItem.company_id == current_user.company_id,
            DictionaryItem.category == item.category,
            DictionaryItem.code == item_in.code
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Item with this code already exists in category")
            
    # Update fields
    update_data = item_in.dict(exclude_unset=True)
    if 'category' in update_data and update_data['category']:
        update_data['category'] = update_data['category'].upper()
        
    for field, value in update_data.items():
        setattr(item, field, value)
        
    db.commit()
    db.refresh(item)
    return item

@router.get("/dictionaries/meta/counts")
async def get_dictionary_counts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get item counts for all categories
    """
    from sqlalchemy import func
    counts = db.query(
        DictionaryItem.category, 
        func.count(DictionaryItem.id)
    ).filter(
        DictionaryItem.company_id == current_user.company_id,
        DictionaryItem.is_active == True
    ).group_by(DictionaryItem.category).all()
    
    return {cat: count for cat, count in counts}

