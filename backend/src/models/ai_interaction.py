from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from backend.src.database.database import Base
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import enum
from sqlalchemy import Enum as SQLEnum


class InteractionType(str, enum.Enum):
    chat = "chat"
    question = "question"
    summary = "summary"
    explanation = "explanation"


class AIInteraction(Base):
    __tablename__ = "ai_interactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey("chapters.id"), nullable=True)  # Optional, can be null for general questions
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    interaction_type = Column(SQLEnum(InteractionType), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    context_used = Column(String, nullable=True)  # JSON string for context
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# Pydantic models for API
class AIInteractionBase(BaseModel):
    user_id: uuid.UUID
    query: str
    response: str
    interaction_type: InteractionType
    timestamp: datetime
    chapter_id: Optional[uuid.UUID] = None
    context_used: Optional[str] = None  # JSON string for context


class AIInteractionCreate(AIInteractionBase):
    pass


class AIInteractionUpdate(BaseModel):
    response: Optional[str] = None
    context_used: Optional[str] = None


class AIInteractionResponse(AIInteractionBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True