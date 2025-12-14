from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from backend.src.database.database import Base
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import enum


class UserRole(str, enum.Enum):
    student = "student"
    educator = "educator"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.student)
    language_preference = Column(String(2), nullable=False, default="en")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    profile_image_url = Column(String, nullable=True)


# Pydantic models for API
class UserBase(BaseModel):
    email: str
    first_name: str
    last_name: str
    language_preference: str = "en"


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language_preference: Optional[str] = None


class UserResponse(UserBase):
    id: uuid.UUID
    role: UserRole
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None
    is_active: bool
    profile_image_url: Optional[str] = None

    class Config:
        from_attributes = True