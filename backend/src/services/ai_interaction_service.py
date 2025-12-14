from typing import List, Optional
from sqlalchemy.orm import Session
from backend.src.models.ai_interaction import AIInteraction, AIInteractionCreate, AIInteractionUpdate


class AIInteractionService:
    """
    Service for managing AI interactions
    """
    
    def create_interaction(self, db: Session, interaction_data: AIInteractionCreate) -> AIInteraction:
        """
        Create a new AI interaction
        """
        interaction = AIInteraction(
            user_id=interaction_data.user_id,
            chapter_id=interaction_data.chapter_id,
            query=interaction_data.query,
            response=interaction_data.response,
            interaction_type=interaction_data.interaction_type,
            timestamp=interaction_data.timestamp,
            context_used=interaction_data.context_used
        )
        db.add(interaction)
        db.commit()
        db.refresh(interaction)
        return interaction
    
    def get_interaction_by_id(self, db: Session, interaction_id: str) -> Optional[AIInteraction]:
        """
        Retrieve an AI interaction by its ID
        """
        return db.query(AIInteraction).filter(AIInteraction.id == interaction_id).first()
    
    def get_interactions_by_user(self, db: Session, user_id: str, skip: int = 0, limit: int = 100) -> List[AIInteraction]:
        """
        Retrieve all AI interactions for a specific user
        """
        return db.query(AIInteraction).filter(AIInteraction.user_id == user_id).offset(skip).limit(limit).all()
    
    def get_interactions_by_chapter(self, db: Session, chapter_id: str, skip: int = 0, limit: int = 100) -> List[AIInteraction]:
        """
        Retrieve all AI interactions for a specific chapter
        """
        return db.query(AIInteraction).filter(AIInteraction.chapter_id == chapter_id).offset(skip).limit(limit).all()
    
    def get_interactions_by_type(self, db: Session, interaction_type: str, skip: int = 0, limit: int = 100) -> List[AIInteraction]:
        """
        Retrieve all AI interactions of a specific type
        """
        return db.query(AIInteraction).filter(AIInteraction.interaction_type == interaction_type).offset(skip).limit(limit).all()
    
    def update_interaction(self, db: Session, interaction_id: str, interaction_data: AIInteractionUpdate) -> Optional[AIInteraction]:
        """
        Update an AI interaction with new data
        """
        interaction = self.get_interaction_by_id(db, interaction_id)
        if interaction:
            for field, value in interaction_data.dict(exclude_unset=True).items():
                setattr(interaction, field, value)
            db.commit()
            db.refresh(interaction)
        return interaction
    
    def delete_interaction(self, db: Session, interaction_id: str) -> bool:
        """
        Delete an AI interaction by its ID
        """
        interaction = self.get_interaction_by_id(db, interaction_id)
        if interaction:
            db.delete(interaction)
            db.commit()
            return True
        return False