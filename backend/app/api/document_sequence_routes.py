from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import DocumentSequence, User
from app.schemas.document_sequence import DocumentSequenceUpdate, DocumentSequenceResponse
from app.api.dependencies import get_current_active_user

router = APIRouter()

@router.get("/document-sequences", response_model=List[DocumentSequenceResponse])
async def list_document_sequences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List all document numbering sequences.
    """
    # Requires admin in a real scenario, but assuming basic access for now
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    return db.query(DocumentSequence).order_by(DocumentSequence.document_type).all()

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
