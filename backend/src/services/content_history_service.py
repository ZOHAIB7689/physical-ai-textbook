from typing import List, Optional
from sqlalchemy.orm import Session
from backend.src.models.content_history import ContentHistory, ContentHistoryCreate
from datetime import datetime


class ContentHistoryService:
    """
    Service for tracking content changes and versions
    """
    
    def create_history_record(self, db: Session, history_data: ContentHistoryCreate) -> ContentHistory:
        """
        Create a new content history record
        """
        history = ContentHistory(
            entity_type=history_data.entity_type,
            entity_id=history_data.entity_id,
            version_number=history_data.version_number,
            content_before=history_data.content_before,
            content_after=history_data.content_after,
            change_summary=history_data.change_summary,
            changed_by=history_data.changed_by,
            change_type=history_data.change_type
        )
        db.add(history)
        db.commit()
        db.refresh(history)
        return history
    
    def get_history_by_entity(self, db: Session, entity_type: str, entity_id: str, skip: int = 0, limit: int = 100) -> List[ContentHistory]:
        """
        Get history records for a specific entity
        """
        return db.query(ContentHistory).filter(
            ContentHistory.entity_type == entity_type,
            ContentHistory.entity_id == entity_id
        ).order_by(ContentHistory.version_number.desc()).offset(skip).limit(limit).all()
    
    def get_history_by_entity_and_type(self, db: Session, entity_type: str, entity_id: str, change_type: str) -> List[ContentHistory]:
        """
        Get history records for a specific entity and change type
        """
        return db.query(ContentHistory).filter(
            ContentHistory.entity_type == entity_type,
            ContentHistory.entity_id == entity_id,
            ContentHistory.change_type == change_type
        ).order_by(ContentHistory.version_number.desc()).all()
    
    def get_latest_version(self, db: Session, entity_type: str, entity_id: str) -> Optional[ContentHistory]:
        """
        Get the latest version of a content item
        """
        return db.query(ContentHistory).filter(
            ContentHistory.entity_type == entity_type,
            ContentHistory.entity_id == entity_id
        ).order_by(ContentHistory.version_number.desc()).first()
    
    def get_version(self, db: Session, entity_type: str, entity_id: str, version_number: int) -> Optional[ContentHistory]:
        """
        Get a specific version of a content item
        """
        return db.query(ContentHistory).filter(
            ContentHistory.entity_type == entity_type,
            ContentHistory.entity_id == entity_id,
            ContentHistory.version_number == version_number
        ).first()
    
    def get_history_by_user(self, db: Session, user_id: str, skip: int = 0, limit: int = 100) -> List[ContentHistory]:
        """
        Get all history records by a specific user
        """
        return db.query(ContentHistory).filter(
            ContentHistory.changed_by == user_id
        ).offset(skip).limit(limit).all()
    
    def get_content_changes_between_versions(self, db: Session, entity_type: str, entity_id: str, from_version: int, to_version: int) -> List[ContentHistory]:
        """
        Get all changes between two specific versions
        """
        return db.query(ContentHistory).filter(
            ContentHistory.entity_type == entity_type,
            ContentHistory.entity_id == entity_id,
            ContentHistory.version_number > from_version,
            ContentHistory.version_number <= to_version
        ).order_by(ContentHistory.version_number.asc()).all()
    
    def calculate_version_number(self, db: Session, entity_type: str, entity_id: str) -> int:
        """
        Calculate the next version number for an entity
        """
        latest = self.get_latest_version(db, entity_type, entity_id)
        if latest:
            return latest.version_number + 1
        return 1  # First version
    
    def create_content_change_record(self, db: Session, entity_type: str, entity_id: str, 
                                   content_before: Optional[str], content_after: str, 
                                   changed_by: str, change_summary: str = "", change_type: str = "update") -> ContentHistory:
        """
        Create a history record for a content change
        """
        version_number = self.calculate_version_number(db, entity_type, entity_id)
        
        history_data = ContentHistoryCreate(
            entity_type=entity_type,
            entity_id=entity_id,
            version_number=version_number,
            content_before=content_before,
            content_after=content_after,
            change_summary=change_summary,
            changed_by=changed_by,
            change_type=change_type
        )
        
        return self.create_history_record(db, history_data)
    
    def get_revision_count(self, db: Session, entity_type: str, entity_id: str) -> int:
        """
        Get the number of revisions for a content item
        """
        return db.query(ContentHistory).filter(
            ContentHistory.entity_type == entity_type,
            ContentHistory.entity_id == entity_id
        ).count()
    
    def revert_to_version(self, db: Session, entity_type: str, entity_id: str, version_number: int, reverted_by: str) -> bool:
        """
        Revert content to a previous version
        This creates a new version based on the old content
        """
        old_version = self.get_version(db, entity_type, entity_id, version_number)
        if not old_version:
            return False
        
        # Get the current version to use as content_before
        current_version = self.get_latest_version(db, entity_type, entity_id)
        current_content = current_version.content_after if current_version else None
        
        # Create a new version with the old content
        new_version_number = self.calculate_version_number(db, entity_type, entity_id)
        
        revert_record = ContentHistory(
            entity_type=entity_type,
            entity_id=entity_id,
            version_number=new_version_number,
            content_before=current_content,
            content_after=old_version.content_after,  # Revert to old content
            change_summary=f"Reverted to version {version_number}",
            changed_by=reverted_by,
            change_type="revert"
        )
        
        db.add(revert_record)
        db.commit()
        return True