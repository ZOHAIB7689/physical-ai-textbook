from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from backend.src.database.database import Base
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LearningSession(Base):
    __tablename__ = "learning_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey("chapters.id"), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    progress_percentage = Column(Integer, nullable=False, default=0)  # 0-100
    last_accessed_page = Column(Integer, default=1)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


# Pydantic models for API
class LearningSessionBase(BaseModel):
    user_id: uuid.UUID
    chapter_id: uuid.UUID
    start_time: datetime
    progress_percentage: int = 0
    last_accessed_page: int = 1
    notes: Optional[str] = None


class LearningSessionCreate(LearningSessionBase):
    pass


class LearningSessionUpdate(BaseModel):
    progress_percentage: Optional[int] = None
    last_accessed_page: Optional[int] = None
    notes: Optional[str] = None
    end_time: Optional[datetime] = None


class LearningSessionResponse(LearningSessionBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    end_time: Optional[datetime] = None

    class Config:
        from_attributes = True