from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.src.database.database import get_db
from backend.src.services.translation_service import TranslationSetService
from backend.src.services.learning_goal_service import LearningGoalService
from backend.src.models.translation_set import TranslationSetCreate, TranslationSetUpdate
from backend.src.models.learning_goal import LearningGoalCreate, LearningGoalUpdate, LearningGoalResponse, GoalStatus
from backend.src.auth.auth import get_current_active_user
from backend.src.models.user import User
from pydantic import BaseModel

router = APIRouter()
translation_service = TranslationSetService()
goal_service = LearningGoalService()

class TranslationRequest(BaseModel):
    entity_type: str
    entity_id: str
    language: str
    translated_content: str
    status: str = "draft"

@router.get("/")
def read_content_management_root():
    return {"message": "Content management services for the Physical AI & Humanoid Robotics Textbook Platform"}

@router.post("/translations")
def create_translation(
    translation_req: TranslationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new translation for content
    """
    # Only allow educators and admins to create translations
    if current_user.role not in ["educator", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only educators and administrators can create translations"
        )

    # Create the translation
    translation_data = TranslationSetCreate(
        entity_type=translation_req.entity_type,
        entity_id=translation_req.entity_id,
        language=translation_req.language,
        translated_content=translation_req.translated_content,
        status=translation_req.status,
        reviewed_by=str(current_user.id) if translation_req.status == "reviewed" else None
    )

    translation = translation_service.create_translation(db, translation_data)
    return translation

@router.put("/translations/{translation_id}")
def update_translation(
    translation_id: str,
    translation_update: TranslationSetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update an existing translation
    """
    # Only allow educators and admins to update translations
    if current_user.role not in ["educator", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only educators and administrators can update translations"
        )

    translation = translation_service.update_translation(db, translation_id, translation_update)
    if not translation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Translation with id {translation_id} not found"
        )

    return translation

@router.get("/translations/{entity_type}/{entity_id}/{language}")
def get_translation(
    entity_type: str,
    entity_id: str,
    language: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a translation for a specific entity and language
    """
    translation = translation_service.get_translation_by_entity_and_language(
        db, entity_type, entity_id, language
    )
    if not translation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No translation found for {entity_type} {entity_id} in {language}"
        )

    return translation

# Learning Goals Endpoints
@router.get("/learning-goals")
def get_learning_goals(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get learning goals for the current user
    """
    goals = goal_service.get_goals_by_user(
        db, str(current_user.id), skip=skip, limit=limit
    )
    return goals

@router.get("/learning-goals/{goal_id}")
def get_learning_goal(
    goal_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific learning goal
    """
    goal = goal_service.get_goal_by_id(db, goal_id)

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Learning goal with id {goal_id} not found"
        )

    # Verify that the goal belongs to the current user
    if str(goal.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this learning goal"
        )

    return goal

@router.post("/learning-goals", response_model=LearningGoalResponse)
def create_learning_goal(
    goal_data: LearningGoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new learning goal
    """
    goal = goal_service.create_goal(db, goal_data, str(current_user.id))
    return goal

@router.put("/learning-goals/{goal_id}", response_model=LearningGoalResponse)
def update_learning_goal(
    goal_id: str,
    goal_update: LearningGoalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a learning goal
    """
    goal = goal_service.get_goal_by_id(db, goal_id)

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Learning goal with id {goal_id} not found"
        )

    # Verify that the goal belongs to the current user
    if str(goal.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this learning goal"
        )

    updated_goal = goal_service.update_goal(db, goal_id, goal_update)
    return updated_goal

@router.delete("/learning-goals/{goal_id}")
def delete_learning_goal(
    goal_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a learning goal
    """
    goal = goal_service.get_goal_by_id(db, goal_id)

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Learning goal with id {goal_id} not found"
        )

    # Verify that the goal belongs to the current user
    if str(goal.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this learning goal"
        )

    success = goal_service.delete_goal(db, goal_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete learning goal"
        )

    return {"message": "Learning goal deleted successfully"}

# Additional Content Management Endpoints for Educators
@router.get("/content-items")
def get_content_items(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get content items that need management (only for educators/admins)
    """
    # Only allow educators and admins
    if current_user.role not in ["educator", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only educators and administrators can manage content"
        )

    # Return modules and chapters that need attention
    from backend.src.services.content_module_service import ContentModuleService
    from backend.src.services.chapter_service import ChapterService

    module_service = ContentModuleService()
    chapter_service = ChapterService()

    modules = module_service.get_all_modules(db, skip=skip, limit=limit)
    chapters = chapter_service.get_all_chapters(db, skip=skip, limit=limit)

    return {
        "modules": modules,
        "chapters": chapters
    }

@router.get("/translations")
def get_all_translations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all translations (only for educators/admins)
    """
    # Only allow educators and admins
    if current_user.role not in ["educator", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only educators and administrators can view translations"
        )

    from backend.src.services.translation_service import TranslationSetService

    service = TranslationSetService()
    translations = service.get_all_translations(db, skip=skip, limit=limit)  # Assuming we have this method

    return translations

# Add get_all_translations method to TranslationSetService
# Update the service to include this method if it doesn't exist

@router.put("/translations/{translation_id}")
def update_translation_status(
    translation_id: str,
    translation_update: TranslationSetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a translation (for status changes like reviewed, approved, etc.)
    """
    # Only allow educators and admins
    if current_user.role not in ["educator", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only educators and administrators can update translations"
        )

    from backend.src.services.translation_service import TranslationSetService

    service = TranslationSetService()
    translation = service.get_translation_by_id(db, translation_id)

    if not translation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Translation with id {translation_id} not found"
        )

    updated_translation = service.update_translation(db, translation_id, translation_update)
    return updated_translation