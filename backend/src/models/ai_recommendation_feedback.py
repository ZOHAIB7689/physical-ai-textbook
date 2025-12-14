from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from backend.src.database.database import Base
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import enum
from sqlalchemy import Enum as SQLEnum


class FeedbackType(str, enum.Enum):
    like = "like"
    dislike = "dislike"
    helpful = "helpful"
    not_helpful = "not_helpful"
    report_inaccurate = "report_inaccurate"
    suggest_improvement = "suggest_improvement"


class AIRecommendationFeedback(Base):
    __tablename__ = "ai_recommendation_feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=False, index=True)
    recommendation_id = Column(String, nullable=False, index=True)  # ID of the recommendation being rated
    feedback_type = Column(SQLEnum(FeedbackType), nullable=False)
    comment = Column(Text, nullable=True)  # Optional detailed feedback
    rating = Column(Integer, nullable=True)  # Optional numeric rating (1-5)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    source_interaction_id = Column(String, nullable=True)  # Link to the original AI interaction


# Pydantic models for API
class AIRecommendationFeedbackBase(BaseModel):
    recommendation_id: str
    feedback_type: FeedbackType
    comment: Optional[str] = None
    rating: Optional[int] = None
    source_interaction_id: Optional[str] = None


class AIRecommendationFeedbackCreate(AIRecommendationFeedbackBase):
    pass


class AIRecommendationFeedbackUpdate(BaseModel):
    feedback_type: Optional[FeedbackType] = None
    comment: Optional[str] = None
    rating: Optional[int] = None


class AIRecommendationFeedbackResponse(AIRecommendationFeedbackBase):
    id: uuid.UUID
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True