from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.src.models.learning_memory import LearningMemoryService as DBLearningMemoryService


class LearningMemoryService:
    """
    Service for maintaining learning memory across sessions for continuity
    This wraps the database model for additional business logic
    """
    
    def __init__(self):
        self.db_service = DBLearningMemoryService()
    
    def preserve_learning_state(self, db: Session, user_id: str, state_data: Dict[str, Any]):
        """
        Preserve the user's current learning state across sessions
        """
        # Save the current learning context
        self.db_service.save_learning_context(db, user_id, state_data)
        
        # Also save specific elements
        if 'current_chapter' in state_data:
            self.db_service.save_memory(
                db, user_id, 'current_state', 'current_chapter', 
                state_data['current_chapter']
            )
        
        if 'reading_position' in state_data:
            self.db_service.save_memory(
                db, user_id, 'current_state', 'reading_position', 
                state_data['reading_position']
            )
        
        if 'last_question' in state_data:
            self.db_service.save_memory(
                db, user_id, 'current_state', 'last_question', 
                state_data['last_question']
            )
        
        # Save progress percentage
        if 'progress_percentage' in state_data:
            self.db_service.save_memory(
                db, user_id, 'progress', 'current_progress', 
                state_data['progress_percentage']
            )
    
    def restore_learning_state(self, db: Session, user_id: str) -> Dict[str, Any]:
        """
        Restore the user's learning state from memory
        """
        # Get the complete learning context
        context = self.db_service.get_learning_context(db, user_id) or {}
        
        # Get additional specific elements
        current_chapter = self.db_service.get_memory(db, user_id, 'current_state', 'current_chapter')
        reading_position = self.db_service.get_memory(db, user_id, 'current_state', 'reading_position')
        last_question = self.db_service.get_memory(db, user_id, 'current_state', 'last_question')
        progress_percentage = self.db_service.get_memory(db, user_id, 'progress', 'current_progress')
        
        # Combine all elements into a state object
        state = {
            **context,
            'current_chapter': current_chapter,
            'reading_position': reading_position,
            'last_question': last_question,
            'progress_percentage': progress_percentage
        }
        
        return {k: v for k, v in state.items() if v is not None}
    
    def save_user_learning_preferences(self, db: Session, user_id: str, preferences: Dict[str, Any]):
        """
        Save user's learning preferences for continuity across sessions
        """
        self.db_service.save_user_preferences(db, user_id, preferences)
        
        # Also save individual preferences separately for easier access
        for key, value in preferences.items():
            self.db_service.save_memory(
                db, user_id, 'preferences', key, value
            )
    
    def get_user_learning_preferences(self, db: Session, user_id: str) -> Dict[str, Any]:
        """
        Retrieve user's learning preferences
        """
        return self.db_service.get_user_preferences(db, user_id) or {}
    
    def save_reading_session_data(self, db: Session, user_id: str, chapter_id: str, session_data: Dict[str, Any]):
        """
        Save data about a reading session for continuity
        """
        # Save last reading position
        if 'position' in session_data:
            self.db_service.save_reading_position(db, user_id, chapter_id, session_data['position'])
        
        # Save session metadata
        self.db_service.save_memory(
            db, user_id, 'reading_sessions', f'session_{chapter_id}', 
            session_data
        )
    
    def get_reading_session_data(self, db: Session, user_id: str, chapter_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve data from a reading session
        """
        return self.db_service.get_memory(db, user_id, 'reading_sessions', f'session_{chapter_id}')
    
    def add_to_conversation_memory(self, db: Session, user_id: str, message: Dict[str, Any]):
        """
        Add a message to the conversation memory for continuity
        """
        self.db_service.save_interaction_history(db, user_id, message)
    
    def get_conversation_memory(self, db: Session, user_id: str) -> list:
        """
        Retrieve the conversation memory
        """
        return self.db_service.get_interaction_history(db, user_id) or []
    
    def clear_user_memory(self, db: Session, user_id: str):
        """
        Clear all memory for a user (e.g., when they want a fresh start)
        """
        # This would involve deleting all memory entries for the user
        # In a real implementation, we'd have a method to delete all records for a user
        # For now, we'll just return, as the full implementation would require
        # more complex database operations
        pass
    
    def transfer_memory_to_new_session(self, db: Session, user_id: str, current_session_id: str, new_session_id: str):
        """
        Transfer relevant memory from one session to another
        """
        # Get all memory for the user
        all_memory = self.db_service.get_all_memory_for_user(db, user_id)
        
        # Identify memory that should be transferred (not session-specific)
        translatable_memory = {
            k: v for k, v in all_memory.items() 
            if not k.startswith('session_')  # Exclude session-specific memory
        }
        
        # Save the translatable memory with session context
        for key, value in translatable_memory.items():
            memory_type, memory_key = key.split(':', 1)
            self.db_service.save_memory(
                db, user_id, f"{memory_type}_for_session", 
                f"{new_session_id}_{memory_key}", value
            )