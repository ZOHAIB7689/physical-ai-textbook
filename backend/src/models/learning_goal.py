from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from backend.src.database.database import Base
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import enum
from sqlalchemy import Enum as SQLEnum


class GoalStatus(str, enum.Enum):
    not_started = "not_started"
    in_progress = "in_progress"
    completed = "completed"
    on_hold = "on_hold"


class LearningGoal(Base):
    __tablename__ = "learning_goals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    target_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(SQLEnum(GoalStatus), nullable=False, default=GoalStatus.not_started)
    progress_percentage = Column(Integer, nullable=False, default=0)  # 0-100
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)


# Pydantic models for API
class LearningGoalBase(BaseModel):
    title: str
    description: Optional[str] = None
    target_date: Optional[datetime] = None
    progress_percentage: int = 0


class LearningGoalCreate(LearningGoalBase):
    pass


class LearningGoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    target_date: Optional[datetime] = None
    status: Optional[GoalStatus] = None
    progress_percentage: Optional[int] = None


class LearningGoalResponse(LearningGoalBase):
    id: uuid.UUID
    user_id: uuid.UUID
    status: GoalStatus
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True