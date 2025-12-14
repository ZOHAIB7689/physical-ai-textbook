from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from backend.src.database.database import Base
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ContentModule(Base):
    __tablename__ = "content_modules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    module_number = Column(Integer, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    is_published = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)


# Pydantic models for API
class ContentModuleBase(BaseModel):
    title: str
    description: Optional[str] = None
    module_number: int
    slug: str
    is_published: bool = False


class ContentModuleCreate(ContentModuleBase):
    pass


class ContentModuleUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    module_number: Optional[int] = None
    slug: Optional[str] = None
    is_published: Optional[bool] = None


class ContentModuleResponse(ContentModuleBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None

    class Config:
        from_attributes = True