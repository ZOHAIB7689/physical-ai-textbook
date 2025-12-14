from typing import List, Optional
from sqlalchemy.orm import Session
from backend.src.models.translation_set import TranslationSet, TranslationSetUpdate, GoalStatus
from backend.src.services.translation_service import TranslationSetService
from datetime import datetime


class TranslationWorkflowService:
    """
    Service for managing the translation review workflow
    """
    
    def __init__(self):
        self.translation_service = TranslationSetService()
    
    def submit_translation_for_review(self, db: Session, translation_id: str, reviewer_id: str) -> bool:
        """
        Submit a translation for review
        """
        # Get the translation
        translation = self.translation_service.get_translation_by_id(db, translation_id)
        if not translation:
            return False
        
        # Update the translation status to "reviewed" and set the reviewer
        update_data = TranslationSetUpdate(
            status="reviewed",
            reviewed_by=reviewer_id
        )
        
        updated_translation = self.translation_service.update_translation(db, translation_id, update_data)
        return updated_translation is not None
    
    def approve_translation(self, db: Session, translation_id: str, approver_id: str) -> bool:
        """
        Approve a translation after review
        """
        # Get the translation
        translation = self.translation_service.get_translation_by_id(db, translation_id)
        if not translation:
            return False
        
        # Update the translation status to "approved"
        update_data = TranslationSetUpdate(
            status="approved"
        )
        
        updated_translation = self.translation_service.update_translation(db, translation_id, update_data)
        return updated_translation is not None
    
    def request_changes_to_translation(self, db: Session, translation_id: str, reviewer_id: str, feedback: str) -> bool:
        """
        Request changes to a translation
        """
        # Get the translation
        translation = self.translation_service.get_translation_by_id(db, translation_id)
        if not translation:
            return False
        
        # Update the translation status back to "draft" with feedback
        update_data = TranslationSetUpdate(
            status="draft"
        )
        
        updated_translation = self.translation_service.update_translation(db, translation_id, update_data)
        return updated_translation is not None
    
    def get_translations_by_review_status(self, db: Session, status: str, skip: int = 0, limit: int = 100) -> List[TranslationSet]:
        """
        Get translations by review status
        """
        return self.translation_service.get_translations_by_status(db, status, skip, limit)
    
    def get_translations_pending_review(self, db: Session, skip: int = 0, limit: int = 100) -> List[TranslationSet]:
        """
        Get translations pending review (status = 'draft')
        """
        return self.translation_service.get_translations_by_status(db, "draft", skip, limit)
    
    def get_translations_pending_approval(self, db: Session, skip: int = 0, limit: int = 100) -> List[TranslationSet]:
        """
        Get translations pending approval (status = 'reviewed')
        """
        return self.translation_service.get_translations_by_status(db, "reviewed", skip, limit)
    
    def get_translations_by_reviewer(self, db: Session, reviewer_id: str, skip: int = 0, limit: int = 100) -> List[TranslationSet]:
        """
        Get translations associated with a specific reviewer
        """
        return db.query(TranslationSet).filter(
            TranslationSet.reviewed_by == reviewer_id
        ).offset(skip).limit(limit).all()
    
    def get_translation_quality_metrics(self, db: Session, reviewer_id: str = None) -> dict:
        """
        Get quality metrics for translations
        """
        # Get all translations
        all_translations = db.query(TranslationSet).all()
        
        # Filter by reviewer if specified
        if reviewer_id:
            all_translations = [t for t in all_translations if t.reviewed_by == reviewer_id]
        
        # Count by status
        total = len(all_translations)
        draft_count = len([t for t in all_translations if t.status == "draft"])
        reviewed_count = len([t for t in all_translations if t.status == "reviewed"])
        approved_count = len([t for t in all_translations if t.status == "approved"])
        
        # Calculate approval rate
        approval_rate = (approved_count / total * 100) if total > 0 else 0
        
        return {
            "total": total,
            "draft": draft_count,
            "reviewed": reviewed_count,
            "approved": approved_count,
            "approval_rate": approval_rate
        }
    
    def get_translation_review_timeline(self, db: Session, translation_id: str) -> List[dict]:
        """
        Get the review timeline for a translation
        This would typically require a separate audit trail table in a full implementation
        """
        # For now, we'll just return basic info
        translation = self.translation_service.get_translation_by_id(db, translation_id)
        if not translation:
            return []
        
        # In a real implementation, this would return the complete history
        # of changes and reviews for this translation
        return [
            {
                "action": f"Translation created in {translation.language}",
                "timestamp": translation.created_at,
                "actor": "Translator"
            },
            {
                "action": f"Translation updated to {translation.status} status",
                "timestamp": translation.updated_at,
                "actor": translation.reviewed_by or "System"
            }
        ]
    
    def batch_process_translations(self, db: Session, translation_ids: List[str], action: str, actor_id: str) -> List[dict]:
        """
        Batch process multiple translations with the same action
        """
        results = []
        for translation_id in translation_ids:
            success = False
            if action == "submit_for_review":
                success = self.submit_translation_for_review(db, translation_id, actor_id)
            elif action == "approve":
                success = self.approve_translation(db, translation_id, actor_id)
            elif action == "request_changes":
                success = self.request_changes_to_translation(db, translation_id, actor_id, "Changes requested by reviewer")
            else:
                success = False
            
            results.append({
                "translation_id": translation_id,
                "success": success
            })
        
        return results