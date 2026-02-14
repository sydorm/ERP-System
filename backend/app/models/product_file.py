from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel

class ProductFile(BaseModel):
    """
    Product File
    Represents an attachment associated with a product (drawing, photo, PDF).
    """
    __tablename__ = "product_files"
    
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False) # e.g., "image/jpeg", "application/pdf"
    file_url = Column(String(1000), nullable=False)
    size = Column(Integer, nullable=True) # Size in bytes
    
    # Relationships
    product = relationship("Product", backref="files")

    def __repr__(self):
        return f"<ProductFile {self.filename} for {self.product_id}>"
