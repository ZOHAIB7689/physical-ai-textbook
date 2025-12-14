from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from backend.src.database.database import Base
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    content_ur = Column(Text, nullable=True)  # Urdu translation
    chapter_number = Column(Integer, nullable=False)
    module_id = Column(UUID(as_uuid=True), ForeignKey("content_modules.id"), nullable=False)
    slug = Column(String, unique=True, nullable=False)
    is_published = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)
    published_by = Column(String, nullable=True)  # ID of user who published
    unpublish_reason = Column(String, nullable=True)  # Reason for unpublishing
    estimated_reading_time = Column(Integer, nullable=True)  # in minutes


# Pydantic models for API
class ChapterBase(BaseModel):
    title: str
    content: str
    content_ur: Optional[str] = None
    chapter_number: int
    module_id: uuid.UUID
    slug: str
    is_published: bool = False
    estimated_reading_time: Optional[int] = None


class ChapterCreate(ChapterBase):
    published_by: Optional[str] = None


class ChapterUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    content_ur: Optional[str] = None
    chapter_number: Optional[int] = None
    module_id: Optional[uuid.UUID] = None
    slug: Optional[str] = None
    is_published: Optional[bool] = None
    published_by: Optional[str] = None
    unpublish_reason: Optional[str] = None
    estimated_reading_time: Optional[int] = None


class ChapterResponse(ChapterBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None

    class Config:
        from_attributes = True