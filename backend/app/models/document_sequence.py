from sqlalchemy import Column, Integer, String
from app.models.base import Base

class DocumentSequence(Base):
    """
    Модель для зберігання та атомарного оновлення нумерації документів.
    Наприклад, для замовлень, прибуткових накладних тощо.
    """
    __tablename__ = "document_sequences"

    id = Column(Integer, primary_key=True, index=True)
    document_type = Column(String(50), unique=True, index=True, nullable=False)
    prefix = Column(String(20), default="", nullable=False)
    next_number = Column(Integer, default=1, nullable=False)
    padding = Column(Integer, default=5, nullable=False)
