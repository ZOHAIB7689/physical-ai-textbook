from typing import List, Optional
from sqlalchemy.orm import Session
from backend.src.models.content_module import ContentModule, ContentModuleCreate, ContentModuleUpdate
from backend.src.models.chapter import Chapter, ChapterCreate, ChapterUpdate


class ContentManagementService:
    """
    Service for managing textbook content including modules and chapters
    """
    
    def create_module(self, db: Session, module_data: ContentModuleCreate) -> ContentModule:
        """
        Create a new content module
        """
        module = ContentModule(
            title=module_data.title,
            description=module_data.description,
            module_number=module_data.module_number,
            slug=module_data.slug,
            is_published=module_data.is_published
        )
        db.add(module)
        db.commit()
        db.refresh(module)
        return module
    
    def get_module_by_id(self, db: Session, module_id: str) -> Optional[ContentModule]:
        """
        Retrieve a module by its ID
        """
        return db.query(ContentModule).filter(ContentModule.id == module_id).first()
    
    def get_module_by_slug(self, db: Session, slug: str) -> Optional[ContentModule]:
        """
        Retrieve a module by its slug
        """
        return db.query(ContentModule).filter(ContentModule.slug == slug).first()
    
    def get_all_modules(self, db: Session, skip: int = 0, limit: int = 100) -> List[ContentModule]:
        """
        Retrieve all modules with optional pagination
        """
        return db.query(ContentModule).offset(skip).limit(limit).all()
    
    def update_module(self, db: Session, module_id: str, module_data: ContentModuleUpdate) -> Optional[ContentModule]:
        """
        Update a module with new data
        """
        module = self.get_module_by_id(db, module_id)
        if module:
            for field, value in module_data.dict(exclude_unset=True).items():
                setattr(module, field, value)
            db.commit()
            db.refresh(module)
        return module
    
    def delete_module(self, db: Session, module_id: str) -> bool:
        """
        Delete a module by its ID
        """
        module = self.get_module_by_id(db, module_id)
        if module:
            db.delete(module)
            db.commit()
            return True
        return False
    
    def create_chapter(self, db: Session, chapter_data: ChapterCreate) -> Chapter:
        """
        Create a new chapter within a module
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
    
    def get_chapters_by_module(self, db: Session, module_id: str, skip: int = 0, limit: int = 100) -> List[Chapter]:
        """
        Retrieve all chapters for a specific module
        """
        return db.query(Chapter).filter(Chapter.module_id == module_id).offset(skip).limit(limit).all()
    
    def update_chapter(self, db: Session, chapter_id: str, chapter_data: ChapterUpdate) -> Optional[Chapter]:
        """
        Update a chapter with new data
        """
        chapter = self.get_chapter_by_id(db, chapter_id)
        if chapter:
            for field, value in chapter_data.dict(exclude_unset=True).items():
                setattr(chapter, field, value)
            db.commit()
            db.refresh(chapter)
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