from typing import List, Optional
from sqlalchemy.orm import Session
from backend.src.models.content_module import ContentModule, ContentModuleCreate, ContentModuleUpdate
from backend.src.models.chapter import Chapter


class ContentModuleService:
    """
    Service for managing content modules
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
    
    def get_all_modules(self, db: Session, skip: int = 0, limit: int = 100, published_only: bool = True) -> List[ContentModule]:
        """
        Retrieve all modules with optional pagination
        """
        query = db.query(ContentModule)
        if published_only:
            query = query.filter(ContentModule.is_published == True)
        return query.offset(skip).limit(limit).all()
    
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
    
    def get_module_with_chapters(self, db: Session, module_id: str) -> Optional[ContentModule]:
        """
        Retrieve a module with its associated chapters
        """
        return db.query(ContentModule).filter(ContentModule.id == module_id).first()