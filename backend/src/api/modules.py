from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from backend.src.database.database import get_db
from backend.src.models.content_module import ContentModuleResponse, ContentModule
from backend.src.services.content_module_service import ContentModuleService
from backend.src.auth.auth import get_current_active_user
from backend.src.models.user import User

router = APIRouter()
service = ContentModuleService()

@router.get("/", response_model=List[ContentModuleResponse])
def get_all_modules(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve all content modules
    """
    modules = service.get_all_modules(db, skip=skip, limit=limit)
    return modules


@router.get("/{module_id}", response_model=ContentModuleResponse)
def get_module_by_id(
    module_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve a specific module by ID
    """
    module = service.get_module_by_id(db, module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module with id {module_id} not found"
        )
    return module


@router.get("/slug/{slug}", response_model=ContentModuleResponse)
def get_module_by_slug(
    slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve a specific module by slug
    """
    module = service.get_module_by_slug(db, slug)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module with slug {slug} not found"
        )
    return module