import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class AuditLog(Base):
    """Append-only record of who accessed what, and when.
guest
    Written synchronously on every read/download of patient data —
    this is an access-accountability log, distinct from Temporal's
    workflow execution history (which tracks pipeline processing,
    not human access).
    """

    __tablename__ = "audit_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=True)
    action = Column(String, nullable=False)  # e.g. "viewed", "downloaded"
    occurred_at = Column(DateTime, default=datetime.utcnow)
