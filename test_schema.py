import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath('backend'))

from app.schemas.document_sequence import DocumentSequenceResponse
from app.models.document_sequence import DocumentSequence

# Create a mock sqlalchemy object
seq = DocumentSequence(id=1, document_type="test", prefix="T-", next_number=1, padding=5)

try:
    resp = DocumentSequenceResponse.model_validate(seq)
    print("Serialization Successful!", resp.model_dump())
except Exception as e:
    import traceback
    traceback.print_exc()
