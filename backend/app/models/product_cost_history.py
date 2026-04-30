from sqlalchemy import Column, String, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from .base import BaseModel


class ProductCostHistory(BaseModel):
    """Stores a record every time a product's cost price is updated via a purchase receipt."""
    __tablename__ = "product_cost_history"

    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("product_variants.id", ondelete="SET NULL"), nullable=True)

    # Source document
    document_type = Column(String(50), nullable=False)   # PurchaseReceipt
    document_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    document_number = Column(String(100), nullable=False)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("counterparties.id", ondelete="SET NULL"), nullable=True)

    # Snapshot before / after
    old_stock = Column(Numeric(15, 4), nullable=False, default=0)
    old_cost = Column(Numeric(15, 2), nullable=True)
    incoming_qty = Column(Numeric(15, 4), nullable=False)
    incoming_price = Column(Numeric(15, 2), nullable=False)
    new_cost = Column(Numeric(15, 2), nullable=False)

    method = Column(String(30), nullable=False)          # last_price | weighted_average
    changed_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
