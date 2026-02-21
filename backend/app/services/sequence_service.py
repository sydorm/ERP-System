from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.document_sequence import DocumentSequence

class SequenceService:
    @staticmethod
    def get_next_number(db: Session, doc_type: str, default_prefix: str = "", default_padding: int = 5) -> str:
        """
        Отримує наступний номер для вказаного типу документа з атомарним блокуванням.
        Якщо запис для послідовності не існує, він створюється автоматично.
        """
        # Block the row for update. This ensures no two transactions will read the same 'next_number'.
        sequence = db.execute(
            select(DocumentSequence)
            .where(DocumentSequence.document_type == doc_type)
            .with_for_update()
        ).scalar_one_or_none()

        if not sequence:
            # Create a new sequence entry
            sequence = DocumentSequence(
                document_type=doc_type,
                prefix=default_prefix,
                next_number=1,
                padding=default_padding
            )
            db.add(sequence)
            db.flush() # flush to get the id if necessary, and let the row exist for future updates

        # Format the number: prefix + zero-padded number
        number_str = f"{sequence.prefix}{str(sequence.next_number).zfill(sequence.padding)}"
        
        # Increment for the next call
        sequence.next_number += 1
        db.flush()

        return number_str
