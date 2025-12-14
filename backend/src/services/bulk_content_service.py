import json
import csv
from io import StringIO
from typing import List, Dict, Any, Union
from sqlalchemy.orm import Session
from backend.src.services.chapter_service import ChapterService
from backend.src.services.content_module_service import ContentModuleService
from backend.src.models.chapter import Chapter
from backend.src.models.content_module import ContentModule


class BulkContentService:
    """
    Service for bulk import/export of content
    """
    
    def __init__(self):
        self.chapter_service = ChapterService()
        self.module_service = ContentModuleService()
    
    def export_chapters_to_json(self, db: Session, module_id: str = None, include_unpublished: bool = False) -> str:
        """
        Export chapters to JSON format
        """
        chapters = []
        
        if module_id:
            chapters = self.chapter_service.get_chapters_by_module(
                db, module_id, skip=0, limit=10000, 
                published_only=not include_unpublished
            )
        else:
            chapters = self.chapter_service.get_all_chapters(
                db, skip=0, limit=10000, 
                published_only=not include_unpublished
            )
        
        # Convert chapters to JSON-serializable format
        chapters_data = []
        for chapter in chapters:
            chapter_dict = {
                "id": str(chapter.id),
                "title": chapter.title,
                "content": chapter.content,
                "content_ur": chapter.content_ur,
                "chapter_number": chapter.chapter_number,
                "module_id": str(chapter.module_id),
                "slug": chapter.slug,
                "is_published": chapter.is_published,
                "estimated_reading_time": chapter.estimated_reading_time,
                "created_at": chapter.created_at.isoformat() if chapter.created_at else None,
                "updated_at": chapter.updated_at.isoformat() if chapter.updated_at else None
            }
            chapters_data.append(chapter_dict)
        
        return json.dumps(chapters_data, indent=2, ensure_ascii=False)
    
    def export_chapters_to_csv(self, db: Session, module_id: str = None, include_unpublished: bool = False) -> str:
        """
        Export chapters to CSV format
        """
        chapters = []
        
        if module_id:
            chapters = self.chapter_service.get_chapters_by_module(
                db, module_id, skip=0, limit=10000, 
                published_only=not include_unpublished
            )
        else:
            chapters = self.chapter_service.get_all_chapters(
                db, skip=0, limit=10000, 
                published_only=not include_unpublished
            )
        
        # Create CSV content
        output = StringIO()
        fieldnames = [
            "id", "title", "content", "content_ur", "chapter_number", 
            "module_id", "slug", "is_published", "estimated_reading_time",
            "created_at", "updated_at"
        ]
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for chapter in chapters:
            writer.writerow({
                "id": str(chapter.id),
                "title": chapter.title,
                "content": chapter.content,
                "content_ur": chapter.content_ur,
                "chapter_number": chapter.chapter_number,
                "module_id": str(chapter.module_id),
                "slug": chapter.slug,
                "is_published": chapter.is_published,
                "estimated_reading_time": chapter.estimated_reading_time or "",
                "created_at": chapter.created_at.isoformat() if chapter.created_at else "",
                "updated_at": chapter.updated_at.isoformat() if chapter.updated_at else ""
            })
        
        return output.getvalue()
    
    def import_chapters_from_json(self, db: Session, json_content: str, user_id: str) -> Dict[str, Any]:
        """
        Import chapters from JSON format
        """
        try:
            chapters_data = json.loads(json_content)
        except json.JSONDecodeError:
            return {"success": False, "error": "Invalid JSON format"}
        
        imported_count = 0
        errors = []
        
        for i, chapter_data in enumerate(chapters_data):
            try:
                # Check if a chapter with this ID already exists
                existing_chapter = self.chapter_service.get_chapter_by_id(db, chapter_data["id"])
                
                from backend.src.models.chapter import ChapterCreate, ChapterUpdate
                from uuid import UUID
                
                if existing_chapter:
                    # Update existing chapter
                    chapter_update = ChapterUpdate(
                        title=chapter_data.get("title"),
                        content=chapter_data.get("content"),
                        content_ur=chapter_data.get("content_ur"),
                        chapter_number=chapter_data.get("chapter_number"),
                        module_id=UUID(chapter_data["module_id"]),
                        slug=chapter_data.get("slug"),
                        is_published=chapter_data.get("is_published", False),
                        estimated_reading_time=chapter_data.get("estimated_reading_time")
                    )
                    
                    updated_chapter = self.chapter_service.update_chapter(db, chapter_data["id"], chapter_update)
                    if updated_chapter:
                        imported_count += 1
                    else:
                        errors.append(f"Failed to update chapter at index {i}")
                else:
                    # Create new chapter
                    chapter_create = ChapterCreate(
                        title=chapter_data["title"],
                        content=chapter_data["content"],
                        content_ur=chapter_data.get("content_ur"),
                        chapter_number=chapter_data["chapter_number"],
                        module_id=UUID(chapter_data["module_id"]),
                        slug=chapter_data["slug"],
                        is_published=chapter_data.get("is_published", False),
                        estimated_reading_time=chapter_data.get("estimated_reading_time"),
                        published_by=user_id
                    )
                    
                    created_chapter = self.chapter_service.create_chapter(db, chapter_create)
                    if created_chapter:
                        imported_count += 1
                    else:
                        errors.append(f"Failed to create chapter at index {i}")
            except Exception as e:
                errors.append(f"Error processing chapter at index {i}: {str(e)}")
        
        return {
            "success": True,
            "imported_count": imported_count,
            "errors": errors
        }
    
    def import_chapters_from_csv(self, db: Session, csv_content: str, user_id: str) -> Dict[str, Any]:
        """
        Import chapters from CSV format
        """
        try:
            # Parse CSV content
            csv_file = StringIO(csv_content)
            reader = csv.DictReader(csv_file)
            chapters_data = list(reader)
        except Exception as e:
            return {"success": False, "error": f"Invalid CSV format: {str(e)}"}
        
        imported_count = 0
        errors = []
        
        for i, row in enumerate(chapters_data):
            try:
                # Check if a chapter with this ID already exists
                existing_chapter = self.chapter_service.get_chapter_by_id(db, row["id"])
                
                from backend.src.models.chapter import ChapterCreate, ChapterUpdate
                from uuid import UUID
                
                if existing_chapter:
                    # Update existing chapter
                    chapter_update = ChapterUpdate(
                        title=row.get("title"),
                        content=row.get("content"),
                        content_ur=row.get("content_ur") or None,
                        chapter_number=int(row["chapter_number"]) if row["chapter_number"] else 0,
                        module_id=UUID(row["module_id"]),
                        slug=row.get("slug"),
                        is_published=row.get("is_published", "False").lower() in ("true", "1", "yes"),
                        estimated_reading_time=int(row["estimated_reading_time"]) if row["estimated_reading_time"] else None
                    )
                    
                    updated_chapter = self.chapter_service.update_chapter(db, row["id"], chapter_update)
                    if updated_chapter:
                        imported_count += 1
                    else:
                        errors.append(f"Failed to update chapter at row {i}")
                else:
                    # Create new chapter
                    chapter_create = ChapterCreate(
                        title=row["title"],
                        content=row["content"],
                        content_ur=row.get("content_ur") or None,
                        chapter_number=int(row["chapter_number"]) if row["chapter_number"] else 0,
                        module_id=UUID(row["module_id"]),
                        slug=row["slug"],
                        is_published=row.get("is_published", "False").lower() in ("true", "1", "yes"),
                        estimated_reading_time=int(row["estimated_reading_time"]) if row["estimated_reading_time"] else None,
                        published_by=user_id
                    )
                    
                    created_chapter = self.chapter_service.create_chapter(db, chapter_create)
                    if created_chapter:
                        imported_count += 1
                    else:
                        errors.append(f"Failed to create chapter at row {i}")
            except Exception as e:
                errors.append(f"Error processing chapter at row {i}: {str(e)}")
        
        return {
            "success": True,
            "imported_count": imported_count,
            "errors": errors
        }
    
    def export_modules_to_json(self, db: Session) -> str:
        """
        Export content modules to JSON format
        """
        modules = self.module_service.get_all_modules(db, skip=0, limit=10000, published_only=False)
        
        modules_data = []
        for module in modules:
            module_dict = {
                "id": str(module.id),
                "title": module.title,
                "description": module.description,
                "module_number": module.module_number,
                "slug": module.slug,
                "is_published": module.is_published,
                "created_at": module.created_at.isoformat() if module.created_at else None,
                "updated_at": module.updated_at.isoformat() if module.updated_at else None,
                "published_at": module.published_at.isoformat() if module.published_at else None
            }
            modules_data.append(module_dict)
        
        return json.dumps(modules_data, indent=2, ensure_ascii=False)
    
    def import_modules_from_json(self, db: Session, json_content: str) -> Dict[str, Any]:
        """
        Import content modules from JSON format
        """
        try:
            modules_data = json.loads(json_content)
        except json.JSONDecodeError:
            return {"success": False, "error": "Invalid JSON format"}
        
        imported_count = 0
        errors = []
        
        from backend.src.models.content_module import ContentModuleCreate, ContentModuleUpdate
        from uuid import UUID
        
        for i, module_data in enumerate(modules_data):
            try:
                # Check if a module with this ID already exists
                existing_module = self.module_service.get_module_by_id(db, module_data["id"])
                
                if existing_module:
                    # Update existing module
                    module_update = ContentModuleUpdate(
                        title=module_data.get("title"),
                        description=module_data.get("description"),
                        module_number=module_data.get("module_number"),
                        slug=module_data.get("slug"),
                        is_published=module_data.get("is_published")
                    )
                    
                    updated_module = self.module_service.update_module(db, module_data["id"], module_update)
                    if updated_module:
                        imported_count += 1
                    else:
                        errors.append(f"Failed to update module at index {i}")
                else:
                    # Create new module
                    module_create = ContentModuleCreate(
                        title=module_data["title"],
                        description=module_data.get("description"),
                        module_number=module_data["module_number"],
                        slug=module_data["slug"],
                        is_published=module_data.get("is_published", False)
                    )
                    
                    created_module = self.module_service.create_module(db, module_create)
                    if created_module:
                        imported_count += 1
                    else:
                        errors.append(f"Failed to create module at index {i}")
            except Exception as e:
                errors.append(f"Error processing module at index {i}: {str(e)}")
        
        return {
            "success": True,
            "imported_count": imported_count,
            "errors": errors
        }
    
    def import_content_package(self, db: Session, package_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Import a complete content package (modules and chapters)
        """
        result = {"modules": {}, "chapters": {}}
        
        # Import modules if provided
        if "modules" in package_data:
            modules_json = json.dumps(package_data["modules"])
            result["modules"] = self.import_modules_from_json(db, modules_json)
        
        # Import chapters if provided
        if "chapters" in package_data:
            chapters_json = json.dumps(package_data["chapters"])
            result["chapters"] = self.import_chapters_from_json(db, chapters_json, user_id)
        
        return result