from typing import List, Optional
from sqlalchemy.orm import Session
from backend.src.models.learning_session import LearningSession, LearningSessionCreate, LearningSessionUpdate


class LearningSessionService:
    """
    Service for managing learning sessions
    """
    
    def create_learning_session(self, db: Session, session_data: LearningSessionCreate) -> LearningSession:
        """
        Create a new learning session
        """
        session = LearningSession(
            user_id=session_data.user_id,
            chapter_id=session_data.chapter_id,
            start_time=session_data.start_time,
            progress_percentage=session_data.progress_percentage,
            last_accessed_page=session_data.last_accessed_page,
            notes=session_data.notes
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session
    
    def get_session_by_id(self, db: Session, session_id: str) -> Optional[LearningSession]:
        """
        Retrieve a learning session by its ID
        """
        return db.query(LearningSession).filter(LearningSession.id == session_id).first()
    
    def get_sessions_by_user(self, db: Session, user_id: str, skip: int = 0, limit: int = 100) -> List[LearningSession]:
        """
        Retrieve all learning sessions for a specific user
        """
        return db.query(LearningSession).filter(LearningSession.user_id == user_id).offset(skip).limit(limit).all()
    
    def get_sessions_by_chapter(self, db: Session, chapter_id: str, skip: int = 0, limit: int = 100) -> List[LearningSession]:
        """
        Retrieve all learning sessions for a specific chapter
        """
        return db.query(LearningSession).filter(LearningSession.chapter_id == chapter_id).offset(skip).limit(limit).all()
    
    def get_session_by_user_and_chapter(self, db: Session, user_id: str, chapter_id: str) -> Optional[LearningSession]:
        """
        Retrieve the learning session for a specific user and chapter
        """
        return db.query(LearningSession).filter(
            LearningSession.user_id == user_id,
            LearningSession.chapter_id == chapter_id
        ).first()
    
    def update_learning_session(self, db: Session, session_id: str, session_data: LearningSessionUpdate) -> Optional[LearningSession]:
        """
        Update a learning session with new data
        """
        session = self.get_session_by_id(db, session_id)
        if session:
            for field, value in session_data.dict(exclude_unset=True).items():
                setattr(session, field, value)
            db.commit()
            db.refresh(session)
        return session
    
    def delete_learning_session(self, db: Session, session_id: str) -> bool:
        """
        Delete a learning session by its ID
        """
        session = self.get_session_by_id(db, session_id)
        if session:
            db.delete(session)
            db.commit()
            return True
        return False
    
    def update_progress(self, db: Session, session_id: str, progress: int, page: int = None) -> Optional[LearningSession]:
        """
        Update the progress of a learning session
        """
        session = self.get_session_by_id(db, session_id)
        if session:
            session.progress_percentage = min(100, max(0, progress))  # Ensure progress is between 0-100
            if page is not None:
                session.last_accessed_page = page
            db.commit()
            db.refresh(session)
        return session