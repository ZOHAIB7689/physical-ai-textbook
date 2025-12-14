from typing import Dict, Any, Optional
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from backend.src.database.database import Base
from pydantic import BaseModel
from datetime import datetime
import json


class LearningMemory(Base):
    __tablename__ = "learning_memory"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=False, index=True)
    session_id = Column(String, nullable=True)  # Optional: tie to specific session
    memory_type = Column(String, nullable=False)  # e.g., "context", "preferences", "progress_state"
    key = Column(String, nullable=False)  # Specific memory key
    value = Column(Text, nullable=False)  # JSON string for flexible value storage
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


# Pydantic model for API
class LearningMemoryBase(BaseModel):
    user_id: str
    memory_type: str
    key: str
    value: str


class LearningMemoryCreate(LearningMemoryBase):
    session_id: Optional[str] = None


class LearningMemoryUpdate(BaseModel):
    value: str


class LearningMemoryResponse(LearningMemoryBase):
    id: uuid.UUID
    session_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LearningMemoryService:
    """
    Service for maintaining learning memory across sessions for continuity
    """
    
    def save_memory(self, db, user_id: str, memory_type: str, key: str, value: Any, session_id: str = None):
        """
        Save a piece of learning memory for a user
        """
        import json
        
        memory_value = json.dumps(value) if not isinstance(value, str) else value
        
        # Check if memory already exists
        existing_memory = db.query(LearningMemory).filter(
            LearningMemory.user_id == user_id,
            LearningMemory.memory_type == memory_type,
            LearningMemory.key == key
        ).first()
        
        if existing_memory:
            # Update existing memory
            existing_memory.value = memory_value
            existing_memory.session_id = session_id
            existing_memory.updated_at = func.now()
        else:
            # Create new memory
            memory = LearningMemory(
                user_id=user_id,
                memory_type=memory_type,
                key=key,
                value=memory_value,
                session_id=session_id
            )
            db.add(memory)
        
        db.commit()
    
    def get_memory(self, db, user_id: str, memory_type: str, key: str) -> Optional[Any]:
        """
        Retrieve a piece of learning memory for a user
        """
        import json
        
        memory = db.query(LearningMemory).filter(
            LearningMemory.user_id == user_id,
            LearningMemory.memory_type == memory_type,
            LearningMemory.key == key
        ).first()
        
        if memory:
            try:
                return json.loads(memory.value)
            except json.JSONDecodeError:
                # If it's not JSON, return as string
                return memory.value
        
        return None
    
    def get_all_memory_for_user(self, db, user_id: str, memory_type: str = None) -> Dict[str, Any]:
        """
        Retrieve all learning memory for a user (optionally filtered by type)
        """
        import json
        
        query = db.query(LearningMemory).filter(LearningMemory.user_id == user_id)
        
        if memory_type:
            query = query.filter(LearningMemory.memory_type == memory_type)
        
        memories = query.all()
        
        result = {}
        for memory in memories:
            try:
                value = json.loads(memory.value)
            except json.JSONDecodeError:
                value = memory.value
            result[f"{memory.memory_type}:{memory.key}"] = value
        
        return result
    
    def clear_memory(self, db, user_id: str, memory_type: str, key: str) -> bool:
        """
        Remove a specific piece of learning memory
        """
        memory = db.query(LearningMemory).filter(
            LearningMemory.user_id == user_id,
            LearningMemory.memory_type == memory_type,
            LearningMemory.key == key
        ).first()
        
        if memory:
            db.delete(memory)
            db.commit()
            return True
        
        return False
    
    def save_learning_context(self, db, user_id: str, context: Dict[str, Any]):
        """
        Save the user's current learning context
        """
        self.save_memory(
            db, 
            user_id, 
            "context", 
            "current_session", 
            context
        )
    
    def get_learning_context(self, db, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve the user's learning context
        """
        return self.get_memory(db, user_id, "context", "current_session")
    
    def save_user_preferences(self, db, user_id: str, preferences: Dict[str, Any]):
        """
        Save the user's preferences for continuity
        """
        self.save_memory(
            db, 
            user_id, 
            "preferences", 
            "user_settings", 
            preferences
        )
    
    def get_user_preferences(self, db, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve the user's preferences
        """
        return self.get_memory(db, user_id, "preferences", "user_settings")
    
    def save_reading_position(self, db, user_id: str, chapter_id: str, position: int):
        """
        Save the user's reading position in a chapter
        """
        self.save_memory(
            db, 
            user_id, 
            "progress", 
            f"chapter_{chapter_id}_position", 
            position
        )
    
    def get_reading_position(self, db, user_id: str, chapter_id: str) -> Optional[int]:
        """
        Retrieve the user's reading position in a chapter
        """
        return self.get_memory(db, user_id, "progress", f"chapter_{chapter_id}_position")
    
    def save_interaction_history(self, db, user_id: str, interaction_data: Dict[str, Any]):
        """
        Save the user's interaction history for continuity
        """
        # Get existing history
        history = self.get_interaction_history(db, user_id) or []
        
        # Add new interaction
        history.append({
            **interaction_data,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only the last 50 interactions to avoid memory bloat
        if len(history) > 50:
            history = history[-50:]
        
        self.save_memory(
            db, 
            user_id, 
            "interactions", 
            "chat_history", 
            history
        )
    
    def get_interaction_history(self, db, user_id: str) -> Optional[list]:
        """
        Retrieve the user's interaction history
        """
        return self.get_memory(db, user_id, "interactions", "chat_history")