from typing import List, Optional
from sqlalchemy.orm import Session
from backend.src.models.translation_set import TranslationSet, TranslationSetCreate, TranslationSetUpdate


class TranslationSetService:
    """
    Service for managing translation sets
    """
    
    def create_translation(self, db: Session, translation_data: TranslationSetCreate) -> TranslationSet:
        """
        Create a new translation set
        """
        translation = TranslationSet(
            entity_type=translation_data.entity_type,
            entity_id=translation_data.entity_id,
            language=translation_data.language,
            translated_content=translation_data.translated_content,
            status=translation_data.status,
            reviewed_by=translation_data.reviewed_by
        )
        db.add(translation)
        db.commit()
        db.refresh(translation)
        return translation
    
    def get_translation_by_id(self, db: Session, translation_id: str) -> Optional[TranslationSet]:
        """
        Retrieve a translation set by its ID
        """
        return db.query(TranslationSet).filter(TranslationSet.id == translation_id).first()
    
    def get_translation_by_entity_and_language(self, db: Session, entity_type: str, entity_id: str, language: str) -> Optional[TranslationSet]:
        """
        Retrieve a translation for a specific entity and language
        """
        return db.query(TranslationSet).filter(
            TranslationSet.entity_type == entity_type,
            TranslationSet.entity_id == entity_id,
            TranslationSet.language == language
        ).first()
    
    def get_translations_by_entity(self, db: Session, entity_type: str, entity_id: str, skip: int = 0, limit: int = 100) -> List[TranslationSet]:
        """
        Retrieve all translations for a specific entity
        """
        return db.query(TranslationSet).filter(
            TranslationSet.entity_type == entity_type,
            TranslationSet.entity_id == entity_id
        ).offset(skip).limit(limit).all()
    
    def get_translations_by_language(self, db: Session, language: str, skip: int = 0, limit: int = 100) -> List[TranslationSet]:
        """
        Retrieve all translations in a specific language
        """
        return db.query(TranslationSet).filter(TranslationSet.language == language).offset(skip).limit(limit).all()
    
    def update_translation(self, db: Session, translation_id: str, translation_data: TranslationSetUpdate) -> Optional[TranslationSet]:
        """
        Update a translation set with new data
        """
        translation = self.get_translation_by_id(db, translation_id)
        if translation:
            for field, value in translation_data.dict(exclude_unset=True).items():
                setattr(translation, field, value)
            db.commit()
            db.refresh(translation)
        return translation
    
    def delete_translation(self, db: Session, translation_id: str) -> bool:
        """
        Delete a translation set by its ID
        """
        translation = self.get_translation_by_id(db, translation_id)
        if translation:
            db.delete(translation)
            db.commit()
            return True
        return False
    
    def get_approved_translations(self, db: Session, entity_type: str, entity_id: str, language: str) -> Optional[TranslationSet]:
        """
        Retrieve approved translations for an entity and language
        """
        return db.query(TranslationSet).filter(
            TranslationSet.entity_type == entity_type,
            TranslationSet.entity_id == entity_id,
            TranslationSet.language == language,
            TranslationSet.status == 'approved'
        ).first()

    def get_all_translations(self, db: Session, skip: int = 0, limit: int = 100) -> List[TranslationSet]:
        """
        Retrieve all translations with optional pagination
        """
        return db.query(TranslationSet).offset(skip).limit(limit).all()

    def get_translation_status_report(self, db: Session, language: str = None, module_id: str = None) -> Dict[str, Any]:
        """
        Generate a translation status report showing progress
        """
        query = db.query(TranslationSet)

        if language:
            query = query.filter(TranslationSet.language == language)

        if module_id:
            # Assuming translations are linked to chapters which are linked to modules
            # This would require joining or additional logic in a real implementation
            pass

        all_translations = query.all()

        # Count translations by status
        status_counts = {}
        for translation in all_translations:
            status = translation.status.value if hasattr(translation.status, 'value') else translation.status
            status_counts[status] = status_counts.get(status, 0) + 1

        total = len(all_translations)
        draft_count = status_counts.get('draft', 0)
        reviewed_count = status_counts.get('reviewed', 0)
        approved_count = status_counts.get('approved', 0)

        # Calculate percentages
        draft_percent = (draft_count / total * 100) if total > 0 else 0
        reviewed_percent = (reviewed_count / total * 100) if total > 0 else 0
        approved_percent = (approved_count / total * 100) if total > 0 else 0

        return {
            "total_translations": total,
            "statuses": {
                "draft": {
                    "count": draft_count,
                    "percentage": round(draft_percent, 2)
                },
                "reviewed": {
                    "count": reviewed_count,
                    "percentage": round(reviewed_percent, 2)
                },
                "approved": {
                    "count": approved_count,
                    "percentage": round(approved_percent, 2)
                }
            },
            "progress_percentage": round(approved_percent, 2)
        }

    def get_translation_completion_report_by_module(self, db: Session, module_id: str) -> Dict[str, Any]:
        """
        Generate a report showing translation progress by module
        """
        # This would need to join with chapters to determine module relationships
        # For now, we'll return a basic structure

        # In a real implementation, you would need to join translations with chapters,
        # then with modules to determine what has been translated for each module

        # This is a simplified implementation for demonstration
        query = db.query(TranslationSet)

        # In a real implementation, we would join with chapters and modules to get
        # the relationship between translations and modules
        all_translations = query.all()

        return {
            "module_id": module_id,
            "translations": len(all_translations),
            "by_status": {
                "draft": 0,
                "reviewed": 0,
                "approved": 0
            }
        }

    def get_top_contributors(self, db: Session, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the top contributors to translations
        """
        from sqlalchemy import func

        # Query to count translations by reviewer
        contributor_counts = db.query(
            TranslationSet.reviewed_by,
            func.count(TranslationSet.id).label('count')
        ).group_by(
            TranslationSet.reviewed_by
        ).order_by(
            func.count(TranslationSet.id).desc()
        ).limit(limit).all()

        return [{"contributor_id": cc[0], "translation_count": cc[1]} for cc in contributor_counts if cc[0]]