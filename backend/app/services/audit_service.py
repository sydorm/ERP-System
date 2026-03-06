import uuid
from typing import Any, Dict, Optional, Type
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog
from app.models.base import BaseModel

class AuditService:
    @staticmethod
    def _serialize_for_json(val: Any) -> Any:
        import decimal
        import datetime as dt
        if isinstance(val, dict):
            return {k: AuditService._serialize_for_json(v) for k, v in val.items()}
        elif isinstance(val, list):
            return [AuditService._serialize_for_json(v) for v in val]
        elif isinstance(val, (datetime, dt.date, uuid.UUID, decimal.Decimal)):
            return str(val)
        return val

    @staticmethod
    def get_dict(obj: BaseModel, relationships: list = None) -> Dict[str, Any]:
        """Convert SQLAlchemy model to a dictionary safely, including optional relationships."""
        data = {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
        if relationships:
            for rel in relationships:
                rel_val = getattr(obj, rel, None)
                if isinstance(rel_val, list):
                    data[rel] = [{c.name: getattr(item, c.name) for c in item.__table__.columns} for item in rel_val]
                elif rel_val is not None:
                    data[rel] = {c.name: getattr(rel_val, c.name) for c in rel_val.__table__.columns}
                else:
                    data[rel] = None
        return data

    @staticmethod
    def compare_and_log(
        db: Session,
        entity_type: str,
        entity_id: uuid.UUID,
        user_id: Optional[uuid.UUID],
        action: str,
        old_obj: Optional[Dict[str, Any]] = None,
        new_obj: Optional[Dict[str, Any]] = None,
        ignore_fields: list = ["updated_at", "created_at"]
    ) -> Optional[AuditLog]:
        """
        Compare old and new object dictionaries and log the differences.
        """
        changes = {}

        if action in ("CREATE", "POST") and new_obj:
            changes = {k: {"old": None, "new": AuditService._serialize_for_json(v)} for k, v in new_obj.items() if k not in ignore_fields and v is not None}
        elif action in ("DELETE", "UNPOST") and old_obj:
            changes = {k: {"old": AuditService._serialize_for_json(v), "new": None} for k, v in old_obj.items() if k not in ignore_fields and v is not None}
        elif old_obj and new_obj:
            for key in new_obj.keys():
                if key in ignore_fields:
                    continue
                old_val = old_obj.get(key)
                new_val = new_obj.get(key)
                
                # Compare as strings to handle UUID, Decimal, Date, etc easily
                str_old = str(old_val) if old_val is not None else None
                str_new = str(new_val) if new_val is not None else None
                
                if str_old != str_new:
                    changes[key] = {
                        "old": AuditService._serialize_for_json(old_val),
                        "new": AuditService._serialize_for_json(new_val)
                    }

        if not changes and action == "UPDATE":
            return None # No meaningful changes to log

        log_entry = AuditLog(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            user_id=user_id,
            changes=changes
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        return log_entry
