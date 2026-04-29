from sqlalchemy import Column, String, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from .base import BaseModel


class BusinessProcessRule(BaseModel):
    """A rule that defines when to automatically create a document."""
    __tablename__ = "business_process_rules"

    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Trigger
    source_type = Column(String(50), nullable=False)   # crm_lead, production_task
    event_type = Column(String(50), nullable=False)    # status_changed, created, updated
    from_status = Column(String(50), nullable=True)
    to_status = Column(String(50), nullable=False)

    # Action
    action_type = Column(String(50), nullable=False)   # create_customer_order, create_sales_invoice
    mode = Column(String(30), default="ask_confirmation", nullable=False)  # automatic, ask_confirmation, disabled

    # Options
    prevent_duplicates = Column(Boolean, default=True, nullable=False)
    log_execution = Column(Boolean, default=True, nullable=False)

    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)


class DocumentRelation(BaseModel):
    """Stores links between documents created through automation."""
    __tablename__ = "document_relations"

    source_type = Column(String(50), nullable=False, index=True)
    source_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    target_type = Column(String(50), nullable=False)
    target_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    relation_type = Column(String(50), default="created_from", nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)


class AutomationLog(BaseModel):
    """Execution log for every rule evaluation."""
    __tablename__ = "automation_logs"

    rule_id = Column(UUID(as_uuid=True), ForeignKey("business_process_rules.id", ondelete="SET NULL"), nullable=True, index=True)
    event_type = Column(String(50), nullable=False)
    source_type = Column(String(50), nullable=False)
    source_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    action_type = Column(String(50), nullable=True)
    # success, skipped, failed, waiting_confirmation
    status = Column(String(30), nullable=False)
    message = Column(Text, nullable=True)
    created_document_type = Column(String(50), nullable=True)
    created_document_id = Column(UUID(as_uuid=True), nullable=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
