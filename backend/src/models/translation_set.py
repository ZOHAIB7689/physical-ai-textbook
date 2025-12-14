from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from backend.src.database.database import Base
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import enum
from sqlalchemy import Enum as SQLEnum


class EntityType(str, enum.Enum):
    chapter = "chapter"
    ui_component = "ui_component"


class TranslationStatus(str, enum.Enum):
    draft = "draft"
    reviewed = "reviewed"
    approved = "approved"


class TranslationSet(Base):
    __tablename__ = "translation_sets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = Column(SQLEnum(EntityType), nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=False)  # Could be a chapter ID or UI component ID
    language = Column(String(2), nullable=False)  # e.g., "ur" for Urdu
    translated_content = Column(Text, nullable=False)
    status = Column(SQLEnum(TranslationStatus), nullable=False, default=TranslationStatus.draft)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


# Pydantic models for API
class TranslationSetBase(BaseModel):
    entity_type: EntityType
    entity_id: uuid.UUID
    language: str
    translated_content: str
    status: TranslationStatus = TranslationStatus.draft
    reviewed_by: Optional[uuid.UUID] = None


class TranslationSetCreate(TranslationSetBase):
    pass


class TranslationSetUpdate(BaseModel):
    translated_content: Optional[str] = None
    status: Optional[TranslationStatus] = None
    reviewed_by: Optional[uuid.UUID] = None


class TranslationSetResponse(TranslationSetBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True