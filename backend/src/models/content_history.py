from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from backend.src.database.database import Base
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ContentHistory(Base):
    __tablename__ = "content_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = Column(String, nullable=False)  # e.g., "chapter", "module"
    entity_id = Column(String, nullable=False, index=True)  # ID of the content item
    version_number = Column(Integer, nullable=False)  # Version number (1, 2, 3, etc.)
    content_before = Column(Text, nullable=True)  # Content before changes
    content_after = Column(Text, nullable=False)  # Content after changes
    change_summary = Column(String, nullable=True)  # Brief description of changes
    changed_by = Column(String, nullable=False)  # ID of user who made changes
    change_type = Column(String, nullable=False)  # e.g., "creation", "update", "translation", "publish", "unpublish"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, nullable=False, default=True)  # Whether this version is currently active


# Pydantic models for API
class ContentHistoryBase(BaseModel):
    entity_type: str
    entity_id: str
    version_number: int
    content_before: Optional[str] = None
    content_after: str
    change_summary: Optional[str] = None
    changed_by: str
    change_type: str


class ContentHistoryCreate(ContentHistoryBase):
    pass


class ContentHistoryUpdate(BaseModel):
    change_summary: Optional[str] = None
    is_active: Optional[bool] = None


class ContentHistoryResponse(ContentHistoryBase):
    id: uuid.UUID
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True