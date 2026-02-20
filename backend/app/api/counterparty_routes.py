from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.session import get_db
from app.models import Counterparty, User
from app.schemas.counterparty import CounterpartyCreate, CounterpartyUpdate, CounterpartyResponse
from app.api.dependencies import get_current_active_user

router = APIRouter()

@router.get("/counterparties", response_model=List[CounterpartyResponse])
async def list_counterparties(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    is_customer: Optional[bool] = None,
    is_supplier: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List counterparties with filtering.
    """
    query = db.query(Counterparty).filter(Counterparty.company_id == current_user.company_id)
    
    if search:
        query = query.filter(or_(
            Counterparty.name.ilike(f"%{search}%"),
            Counterparty.tax_id.ilike(f"%{search}%")
        ))
        
    if is_customer is not None:
        query = query.filter(Counterparty.is_customer == is_customer)
    
    if is_supplier is not None:
        query = query.filter(Counterparty.is_supplier == is_supplier)
        
    return query.offset(skip).limit(limit).all()

@router.post("/counterparties", response_model=CounterpartyResponse, status_code=status.HTTP_201_CREATED)
async def create_counterparty(
    counterparty_in: CounterpartyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new counterparty.
    """
    counterparty = Counterparty(
        **counterparty_in.dict(),
        company_id=current_user.company_id
    )
    db.add(counterparty)
    db.commit()
    db.refresh(counterparty)
    return counterparty

@router.get("/counterparties/{id}", response_model=CounterpartyResponse)
async def get_counterparty(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a single counterparty.
    """
    counterparty = db.query(Counterparty).filter(
        Counterparty.id == id,
        Counterparty.company_id == current_user.company_id
    ).first()
    
    if not counterparty:
        raise HTTPException(status_code=404, detail="Counterparty not found")
    return counterparty

@router.put("/counterparties/{id}", response_model=CounterpartyResponse)
async def update_counterparty(
    id: UUID,
    counterparty_in: CounterpartyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a counterparty.
    """
    counterparty = db.query(Counterparty).filter(
        Counterparty.id == id,
        Counterparty.company_id == current_user.company_id
    ).first()
    
    if not counterparty:
        raise HTTPException(status_code=404, detail="Counterparty not found")
        
    update_data = counterparty_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(counterparty, field, value)
        
    db.commit()
    db.refresh(counterparty)
    return counterparty

@router.delete("/counterparties/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_counterparty(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a counterparty.
    """
    counterparty = db.query(Counterparty).filter(
        Counterparty.id == id,
        Counterparty.company_id == current_user.company_id
    ).first()
    
    if not counterparty:
        raise HTTPException(status_code=404, detail="Counterparty not found")
        
    db.delete(counterparty)
    db.commit()
    return None
