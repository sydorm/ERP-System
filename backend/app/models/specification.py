import enum
from sqlalchemy import Column, String, Boolean, ForeignKey, Integer, Numeric, Text, JSON, Enum as saEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel

class CalculationDimension(str, enum.Enum):
    HEIGHT = "height_cm"
    WIDTH = "width_cm"
    LENGTH = "length_cm"
    AREA = "area"
    VOLUME = "volume"
    CUSTOM = "custom"

class CalculationType(str, enum.Enum):
    FIXED = "fixed"
    INTERPOLATION = "interpolation"
    AREA = "area"
    VOLUME = "volume"
    FORMULA = "formula"

class ProductSpecification(BaseModel):
    """
    Product Specification (BOM Header)
    Represents a specific recipe or bill of materials for a product.
    """
    __tablename__ = "product_specifications"
    
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False) # e.g., "Стандартна v1", "Економ"
    is_active = Column(Boolean, default=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    notes = Column(Text, nullable=True)
    
    # Relationships
    product = relationship("Product", backref="specifications")
    items = relationship("SpecificationItem", back_populates="specification", cascade="all, delete-orphan")
    stages = relationship("ProductSpecificationStage", back_populates="specification", cascade="all, delete-orphan", order_by="ProductSpecificationStage.sort_order")

    def __repr__(self):
        return f"<Specification {self.name} for {self.product_id}>"

class SpecificationItem(BaseModel):
    """
    Specification Item (BOM Line)
    Represents a component and its quantity in a specification, 
    optionally with smart calculation rules.
    """
    __tablename__ = "specification_items"
    
    specification_id = Column(UUID(as_uuid=True), ForeignKey("product_specifications.id", ondelete="CASCADE"), nullable=False, index=True)
    component_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False) # The component being used
    quantity = Column(Numeric(15, 4), nullable=False, default=1.0)
    unit_of_measure = Column(String(50), nullable=True) # Optional override
    notes = Column(String(500), nullable=True)

    # Merged Smart Calculation Fields
    is_calculated = Column(Boolean, default=False, nullable=False)
    calc_type = Column(saEnum(CalculationType, values_callable=lambda obj: [e.value for e in obj]), nullable=True, default=CalculationType.FIXED)
    calc_dimension = Column(saEnum(CalculationDimension, values_callable=lambda obj: [e.value for e in obj]), nullable=True)
    calc_data_points = Column(JSON, nullable=True)
    calc_dim_config = Column(JSON, nullable=True)
    calc_formula = Column(String(500), nullable=True)
    calc_waste_factor = Column(Numeric(5, 4), nullable=False, default=0.0)
    
    # Detail-specific fields
    line_type = Column(String(20), default="material", nullable=False) # 'material', 'detail'
    size_from_attr = Column(String(100), nullable=True) # Characteristic name to read from
    size_multiplier = Column(Numeric(10, 2), nullable=True, default=1.0)
    fixed_length = Column(Numeric(10, 2), nullable=True)
    fixed_width = Column(Numeric(10, 2), nullable=True)
    
    # Conditional material selection
    mapping_attr = Column(String(100), nullable=True) # e.g., "ДСП"
    material_mapping = Column(JSON, nullable=True) # e.g., {"Сонома": "uuid", "Венге": "uuid"}
    
    # Relationships
    specification = relationship("ProductSpecification", back_populates="items")
    component = relationship("Product", foreign_keys=[component_id])

    def __repr__(self):
        return f"<SpecItem {self.component_id} x {self.quantity}>"


class ProductSpecificationStage(BaseModel):
    """
    Production Stages in a Specification (BOM Stage)
    Defines the labor and time requirements for manufacturing.
    """
    __tablename__ = "specification_stages"
    
    specification_id = Column(UUID(as_uuid=True), ForeignKey("product_specifications.id", ondelete="CASCADE"), nullable=False, index=True)
    stage_id = Column(UUID(as_uuid=True), ForeignKey("dictionary_items.id", ondelete="RESTRICT"), nullable=False)
    duration_hours = Column(Numeric(15, 2), nullable=False, default=0.0)
    brigade_id = Column(UUID(as_uuid=True), ForeignKey("brigades.id", ondelete="RESTRICT"), nullable=True) # References the Brigade
    sort_order = Column(Integer, default=0, nullable=False)

    # Relationships
    specification = relationship("ProductSpecification", back_populates="stages")
    stage = relationship("DictionaryItem", foreign_keys=[stage_id])
    brigade = relationship("Brigade")

    def __repr__(self):
        return f"<SpecStage {self.stage_id} {self.duration_hours}h>"
