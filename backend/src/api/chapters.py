from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from backend.src.database.database import get_db
from backend.src.models.chapter import ChapterResponse, Chapter
from backend.src.services.chapter_service import ChapterService
from backend.src.auth.auth import get_current_active_user
from backend.src.models.user import User
from backend.src.utils.errors import ValidationError

router = APIRouter()
service = ChapterService()

@router.get("/{slug}", response_model=ChapterResponse)
def get_chapter_by_slug(
    slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve a specific chapter by slug
    """
    chapter = service.get_chapter_by_slug(db, slug)
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chapter with slug {slug} not found"
        )
    return chapter

@router.get("/module/{module_id}", response_model=List[ChapterResponse])
def get_chapters_by_module(
    module_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve all chapters for a specific module
    """
    chapters = service.get_chapters_by_module(db, module_id, skip=skip, limit=limit)
    return chapters

@router.get("/{slug}/language/{lang}", response_model=ChapterResponse)
def get_chapter_by_language(
    slug: str,
    lang: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve a specific chapter in a specific language
    """
    chapter = service.get_chapter_by_slug(db, slug)
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chapter with slug {slug} not found"
        )

    # Check if the requested language is available
    if lang == 'ur' and chapter.content_ur:
        # Create a modified response with Urdu content
        chapter_response = ChapterResponse.from_orm(chapter)
        # In a real implementation, we would swap the content based on language
        # For now, we'll just pass the chapter as is and handle language in the frontend
        return chapter_response
    elif lang == 'en':
        return ChapterResponse.from_orm(chapter)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Content in language '{lang}' not available for this chapter"
        )