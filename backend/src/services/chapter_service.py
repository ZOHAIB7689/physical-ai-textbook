from typing import List, Optional
from sqlalchemy.orm import Session
from backend.src.models.chapter import Chapter, ChapterCreate, ChapterUpdate
from backend.src.services.content_history_service import ContentHistoryService
from datetime import datetime


class ChapterService:
    """
    Service for managing chapters
    """

    def __init__(self):
        self.history_service = ContentHistoryService()

    def create_chapter(self, db: Session, chapter_data: ChapterCreate) -> Chapter:
        """
        Create a new chapter
        """
        chapter = Chapter(
            title=chapter_data.title,
            content=chapter_data.content,
            content_ur=chapter_data.content_ur,
            chapter_number=chapter_data.chapter_number,
            module_id=chapter_data.module_id,
            slug=chapter_data.slug,
            is_published=chapter_data.is_published,
            estimated_reading_time=chapter_data.estimated_reading_time
        )
        db.add(chapter)
        db.commit()
        db.refresh(chapter)

        # Create history record for creation
        self.history_service.create_content_change_record(
            db,
            "chapter",
            str(chapter.id),
            None,  # No content before
            chapter.content,
            chapter_data.published_by or "unknown",
            "Chapter created",
            "creation"
        )

        return chapter
    
    def get_chapter_by_id(self, db: Session, chapter_id: str) -> Optional[Chapter]:
        """
        Retrieve a chapter by its ID
        """
        return db.query(Chapter).filter(Chapter.id == chapter_id).first()
    
    def get_chapter_by_slug(self, db: Session, slug: str) -> Optional[Chapter]:
        """
        Retrieve a chapter by its slug
        """
        return db.query(Chapter).filter(Chapter.slug == slug).first()

    def get_chapter_by_slug_with_fallback(self, db: Session, slug: str, preferred_language: str = 'en') -> Optional[Chapter]:
        """
        Retrieve a chapter by its slug with fallback to English if preferred language is not available
        """
        chapter = db.query(Chapter).filter(Chapter.slug == slug).first()

        if chapter and preferred_language == 'ur':
            # If Urdu is requested but not available, fall back to English
            if not chapter.content_ur or not chapter.content_ur.strip():
                # Return chapter with English content marked as fallback
                # In a more complete implementation, we might also look for translations in the TranslationSet
                pass

        return chapter
    
    def get_chapters_by_module(self, db: Session, module_id: str, skip: int = 0, limit: int = 100, published_only: bool = True) -> List[Chapter]:
        """
        Retrieve all chapters for a specific module
        """
        query = db.query(Chapter).filter(Chapter.module_id == module_id)
        if published_only:
            query = query.filter(Chapter.is_published == True)
        return query.offset(skip).limit(limit).all()
    
    def get_all_chapters(self, db: Session, skip: int = 0, limit: int = 100, published_only: bool = True) -> List[Chapter]:
        """
        Retrieve all chapters with optional pagination
        """
        query = db.query(Chapter)
        if published_only:
            query = query.filter(Chapter.is_published == True)
        return query.offset(skip).limit(limit).all()
    
    def update_chapter(self, db: Session, chapter_id: str, chapter_data: ChapterUpdate) -> Optional[Chapter]:
        """
        Update a chapter with new data
        """
        chapter = self.get_chapter_by_id(db, chapter_id)
        if chapter:
            # Save original content for history tracking
            original_content = chapter.content
            original_content_ur = chapter.content_ur

            for field, value in chapter_data.dict(exclude_unset=True).items():
                setattr(chapter, field, value)

            db.commit()
            db.refresh(chapter)

            # Create history record for update
            change_summary = "Chapter content updated"
            if chapter_data.content and chapter_data.content != original_content:
                change_summary = "Chapter content modified"
            elif chapter_data.content_ur and chapter_data.content_ur != original_content_ur:
                change_summary = "Urdu translation updated"
            elif chapter_data.is_published is not None:
                change_summary = "Publication status changed"

            # Determine the type of change
            change_type = "update"
            if chapter_data.is_published is not None:
                change_type = "publishing"  # Changed from "update" to "publishing" for publication status changes
            elif chapter_data.content_ur is not None and chapter_data.content_ur != original_content_ur:
                change_type = "translation"  # Changed for translation updates
            elif chapter_data.content is not None and chapter_data.content != original_content:
                change_type = "content"  # Changed for content updates

            # Use the user ID from the update request if available, otherwise use a generic ID or the chapter's published_by field
            changed_by = getattr(chapter_data, 'changed_by', chapter.published_by or 'system')

            self.history_service.create_content_change_record(
                db,
                "chapter",
                chapter_id,
                original_content,  # Original content before changes
                chapter.content,   # New content after changes
                changed_by,
                change_summary,
                change_type
            )

        return chapter
    
    def delete_chapter(self, db: Session, chapter_id: str) -> bool:
        """
        Delete a chapter by its ID
        """
        chapter = self.get_chapter_by_id(db, chapter_id)
        if chapter:
            db.delete(chapter)
            db.commit()
            return True
        return False

    def publish_chapter(self, db: Session, chapter_id: str, publisher_id: str) -> Optional[Chapter]:
        """
        Publish a chapter
        """
        chapter = self.get_chapter_by_id(db, chapter_id)
        if chapter:
            # Create history record for the publishing action
            self.history_service.create_content_change_record(
                db,
                "chapter",
                chapter_id,
                chapter.content,  # Using content as the before value
                chapter.content,  # Content unchanged, only status changed
                publisher_id,
                "Chapter published",
                "publishing"
            )

            chapter.is_published = True
            chapter.published_at = datetime.utcnow()
            chapter.published_by = publisher_id
            db.commit()
            db.refresh(chapter)
        return chapter

    def unpublish_chapter(self, db: Session, chapter_id: str, reason: str = None) -> Optional[Chapter]:
        """
        Unpublish a chapter
        """
        chapter = self.get_chapter_by_id(db, chapter_id)
        if chapter:
            # Create history record for the unpublishing action
            self.history_service.create_content_change_record(
                db,
                "chapter",
                chapter_id,
                chapter.content,  # Using content as the before value
                chapter.content,  # Content unchanged, only status changed
                chapter.published_by or "system",
                f"Chapter unpublished - reason: {reason or 'No reason provided'}",
                "publishing"
            )

            chapter.is_published = False
            chapter.unpublish_reason = reason
            db.commit()
            db.refresh(chapter)
        return chapter

    def get_published_chapters(self, db: Session, module_id: str = None, skip: int = 0, limit: int = 100) -> List[Chapter]:
        """
        Get all published chapters, optionally filtered by module
        """
        query = db.query(Chapter).filter(Chapter.is_published == True)
        if module_id:
            query = query.filter(Chapter.module_id == module_id)
        return query.offset(skip).limit(limit).all()

    def get_unpublished_chapters(self, db: Session, skip: int = 0, limit: int = 100) -> List[Chapter]:
        """
        Get all unpublished chapters
        """
        return db.query(Chapter).filter(Chapter.is_published == False).offset(skip).limit(limit).all()