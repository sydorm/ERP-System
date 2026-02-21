from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import DocumentSequence, User
from app.schemas.document_sequence import DocumentSequenceUpdate, DocumentSequenceResponse
from app.api.dependencies import get_current_active_user

from sqlalchemy.orm import Session, joinedload

router = APIRouter()

@router.get("/document-sequences", response_model=List[DocumentSequenceResponse])
async def list_document_sequences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List all document numbering sequences. Auto-initializes defaults if missing.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    sequences = db.query(DocumentSequence).order_by(DocumentSequence.document_type).all()
    
    # Auto-initialize if empty (convenience)
    if not sequences:
        defaults = [
            ("order", "ORD-"),
            ("purchase_receipt", "PREC-"),
            ("sales_invoice", "INV-"),
            ("transfer", "TR-"),
            ("inventory", "ST-")
        ]
        for dtype, prefix in defaults:
            seq = DocumentSequence(document_type=dtype, prefix=prefix, next_number=1, padding=5)
            db.add(seq)
        db.commit()
        sequences = db.query(DocumentSequence).order_by(DocumentSequence.document_type).all()

    return sequences

@router.put("/document-sequences/{id}", response_model=DocumentSequenceResponse)
async def update_document_sequence(
    id: int,
    seq_in: DocumentSequenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a document sequence (e.g. prefix, next number, padding).
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    sequence = db.query(DocumentSequence).filter(DocumentSequence.id == id).first()
    if not sequence:
        raise HTTPException(status_code=404, detail="Sequence not found")
        
    update_data = seq_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(sequence, field, value)
        
    db.commit()
    db.refresh(sequence)
    return sequence
