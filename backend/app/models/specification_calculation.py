import enum
import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, Integer, Numeric, Text, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel

class CalculationDimension(str, enum.Enum):
    HEIGHT = "height_cm"
    WIDTH = "width_cm"
    LENGTH = "length_cm"
    CUSTOM = "custom"

class SpecificationCalculationRule(BaseModel):
    """
    Parametric Calculation Rule for a BOM Item.
    Allows calculating quantity based on product dimensions using interpolation.
    """
    __tablename__ = "specification_calculation_rules"
    
    specification_item_id = Column(UUID(as_uuid=True), ForeignKey("specification_items.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # Primary dimension to track (height, width, length)
    dimension = Column(Enum(CalculationDimension), nullable=False, default=CalculationDimension.HEIGHT)
    
    # Data points for interpolation: [{"input": 40, "output": 1.2}, {"input": 50, "output": 1.4}]
    data_points = Column(JSON, nullable=False, default=list)
    
    # Custom formula if dimension is CUSTOM (e.g., "(h * w) / 100")
    formula = Column(String(500), nullable=True)
    
    # Waste percentage (e.g., 0.05 for 5%)
    waste_factor = Column(Numeric(5, 4), nullable=False, default=0.0)
    
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    specification_item = relationship("SpecificationItem", backref="calculation_rule")

    def __repr__(self):
        return f"<CalculationRule for Item {self.specification_item_id}>"
