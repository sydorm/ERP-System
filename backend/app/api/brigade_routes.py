from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.db.session import get_db
from app.models.brigade import Brigade, BrigadeMember
from app.models.hr import Employee
from app.models.user import User
from app.schemas.brigade import (
    BrigadeCreate, BrigadeUpdate, Brigade as BrigadeResponse,
    BrigadeMemberCreate, BrigadeMember as BrigadeMemberResponse
)
from app.api.dependencies import get_current_active_user

router = APIRouter()

@router.get("/brigades", response_model=List[BrigadeResponse])
async def list_brigades(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    stage_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Brigade)
    if search:
        query = query.filter(Brigade.name.ilike(f"%{search}%"))
    if stage_id:
        query = query.filter(Brigade.stage_id == stage_id)
        
    objs = query.offset(skip).limit(limit).all()
    return objs

@router.post("/brigades", response_model=BrigadeResponse, status_code=status.HTTP_201_CREATED)
async def create_brigade(
    brigade_in: BrigadeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    brigade = Brigade(
        name=brigade_in.name,
        stage_id=brigade_in.stage_id,
        is_active=brigade_in.is_active
    )
    db.add(brigade)
    db.flush()
    
    if brigade_in.members:
        for member_in in brigade_in.members:
            member = BrigadeMember(
                **member_in.dict(),
                brigade_id=brigade.id
            )
            db.add(member)
            
    db.commit()
    db.refresh(brigade)
    return brigade

@router.get("/brigades/{id}", response_model=BrigadeResponse)
async def get_brigade(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    brigade = db.query(Brigade).filter(Brigade.id == id).first()
    if not brigade:
        raise HTTPException(status_code=404, detail="Brigade not found")
    return brigade

@router.put("/brigades/{id}", response_model=BrigadeResponse)
async def update_brigade(
    id: UUID,
    brigade_in: BrigadeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    brigade = db.query(Brigade).filter(Brigade.id == id).first()
    if not brigade:
        raise HTTPException(status_code=404, detail="Brigade not found")
        
    update_data = brigade_in.dict(exclude_unset=True, exclude={'members'})
    for field, value in update_data.items():
        setattr(brigade, field, value)
        
    if brigade_in.members is not None:
        # Simple sync: delete and re-add
        db.query(BrigadeMember).filter(BrigadeMember.brigade_id == id).delete()
        for member_in in brigade_in.members:
            member = BrigadeMember(
                **member_in.dict(),
                brigade_id=id
            )
            db.add(member)
            
    db.commit()
    db.refresh(brigade)
    return brigade

@router.delete("/brigades/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_brigade(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    brigade = db.query(Brigade).filter(Brigade.id == id).first()
    if not brigade:
        raise HTTPException(status_code=404, detail="Brigade not found")
    
    db.delete(brigade)
    db.commit()
    return None
