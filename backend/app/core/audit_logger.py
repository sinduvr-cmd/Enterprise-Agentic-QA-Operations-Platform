"""
Audit logger for enterprise compliance, tracking all modifications and agent decisions.
"""
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.app.models.audit import AuditLog
from backend.app.models.user import User

logger = logging.getLogger(__name__)


def record_audit_event(
    db: Session,
    action: str,
    resource_type: str,
    resource_id: str,
    details: Dict[str, Any],
    user: Optional[User] = None,
    project_id: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> AuditLog:
    """
    Creates and commits an immutable audit log record.
    """
    try:
        log_entry = AuditLog(
            user_id=user.id if user else None,
            user_email=user.email if user else "system",
            project_id=project_id,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id),
            details=details,
            ip_address=ip_address,
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        return log_entry
    except Exception as e:
        logger.error(f"Failed to record audit event '{action}': {e}")
        db.rollback()
        raise e
