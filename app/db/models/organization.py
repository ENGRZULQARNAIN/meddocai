import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class Organization(Base):
    """A tenant — e.g. one hospital or clinic."""

    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    plan_tier = Column(String, default="starter")
