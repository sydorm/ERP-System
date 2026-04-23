from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db.session import get_db

from app.schemas.counterparty import (
    CounterpartyCreate, CounterpartyUpdate, CounterpartyResponse,
    BankAccountCreate, BankAccountResponse,
    ContactCreate, ContactResponse,
    CounterpartyMaterialCreate, CounterpartyMaterialResponse
)
from app.api.dependencies import get_current_active_user
from app.models import (
    Counterparty, User, Product,
    CounterpartyBankAccount, CounterpartyContact, CounterpartyMaterial
)

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
    query = db.query(Counterparty).filter(
        Counterparty.company_id == current_user.company_id,
        Counterparty.is_deleted == False
    )
    
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
    
    # Enrichment for materials (add product name)
    for mat in counterparty.materials:
        product = db.query(Product).filter(Product.id == mat.product_id).first()
        if product:
            mat.product_name = product.name
            
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
        
    # Check references
    from app.models import Order, PurchaseOrder
    is_used = db.query(Order).filter(Order.counterparty_id == counterparty.id).first() or \
              db.query(PurchaseOrder).filter(PurchaseOrder.supplier_id == counterparty.id).first()
              
    if is_used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неможливо видалити контрагента, оскільки він має пов'язані замовлення або документи."
        )
        
    counterparty.is_deleted = True
    db.commit()
    return None

# --- Nested Entity Endpoints ---

@router.post("/counterparties/{id}/bank-accounts", response_model=BankAccountResponse)
async def add_bank_account(
    id: UUID,
    account_in: BankAccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    account = CounterpartyBankAccount(**account_in.dict(), counterparty_id=id)
    db.add(account)
    db.commit()
    db.refresh(account)
    return account

@router.delete("/counterparties/{id}/bank-accounts/{account_id}")
async def delete_bank_account(
    id: UUID, account_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    account = db.query(CounterpartyBankAccount).filter(
        CounterpartyBankAccount.id == account_id,
        CounterpartyBankAccount.counterparty_id == id
    ).first()
    if not account:
        raise HTTPException(status_code=404, detail="Bank account not found")
    db.delete(account)
    db.commit()
    return {"status": "ok"}

@router.post("/counterparties/{id}/contacts", response_model=ContactResponse)
async def add_contact(
    id: UUID,
    contact_in: ContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    contact = CounterpartyContact(**contact_in.dict(), counterparty_id=id)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact

@router.delete("/counterparties/{id}/contacts/{contact_id}")
async def delete_contact(
    id: UUID, contact_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    contact = db.query(CounterpartyContact).filter(
        CounterpartyContact.id == contact_id,
        CounterpartyContact.counterparty_id == id
    ).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    db.delete(contact)
    db.commit()
    return {"status": "ok"}

@router.post("/counterparties/{id}/materials", response_model=CounterpartyMaterialResponse)
async def add_material(
    id: UUID,
    material_in: CounterpartyMaterialCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    material = CounterpartyMaterial(**material_in.dict(), counterparty_id=id)
    db.add(material)
    db.commit()
    db.refresh(material)
    
    product = db.query(Product).filter(Product.id == material.product_id).first()
    if product:
        material.product_name = product.name
        
    return material

@router.delete("/counterparties/{id}/materials/{material_id}")
async def delete_material(
    id: UUID, material_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    material = db.query(CounterpartyMaterial).filter(
        CounterpartyMaterial.id == material_id,
        CounterpartyMaterial.counterparty_id == id
    ).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    db.delete(material)
    db.commit()
    return {"status": "ok"}
