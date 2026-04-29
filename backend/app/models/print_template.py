from sqlalchemy import Column, String, Text, Boolean
from .base import BaseModel

class PrintTemplate(BaseModel):
    """
    Document Print Templates (HTML + CSS for standard office docs like BAS/1C)
    """
    __tablename__ = "print_templates"

    name = Column(String(100), nullable=False)
    document_type = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=True)
    html_template = Column(Text, nullable=False)
    css_template = Column(Text, nullable=True)
    is_default = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    def __repr__(self):
        return f"<PrintTemplate {self.name} ({self.document_type})>"
