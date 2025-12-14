from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from backend.src.database.database import get_db
from backend.src.ai.rag_service import RAGService
from backend.src.auth.auth import get_current_active_user
from backend.src.models.user import User
from pydantic import BaseModel
from datetime import datetime
from slowapi import Limiter
from slowapi.util import get_remote_address

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

router = APIRouter()
rag_service = RAGService()

class ChatRequest(BaseModel):
    question: str
    chapter_id: Optional[str] = None
    context: Optional[dict] = None

class ChatResponse(BaseModel):
    answer: str
    references: list
    confidence: float

@router.get("/")
def read_ai_root():
    return {"message": "AI services for the Physical AI & Humanoid Robotics Textbook Platform"}

@router.post("/chat", response_model=ChatResponse)
@limiter.limit("10/minute")  # Limit to 10 requests per minute per IP
def chat_with_bot(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Submit a question to the RAG chatbot and receive an answer
    """
    try:
        response = rag_service.answer_question(
            question=request.question,
            user_id=str(current_user.id),
            chapter_id=request.chapter_id
        )

        return ChatResponse(
            answer=response["answer"],
            references=response["references"],
            confidence=response["confidence"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat request: {str(e)}"
        )

@router.get("/history")
def get_ai_interaction_history(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve the user's AI interaction history
    """
    from backend.src.services.ai_interaction_service import AIInteractionService

    service = AIInteractionService()
    interactions = service.get_interactions_by_user(
        db,
        str(current_user.id),
        skip=skip,
        limit=limit
    )

    return interactions

@router.get("/learning-path")
def get_personalized_learning_path(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get AI-recommended learning path based on user progress
    """
    from backend.src.services.learning_path_service import LearningPathService

    service = LearningPathService()
    learning_path = service.get_learning_path(db, str(current_user.id))

    return learning_path

@router.post("/summary")
@limiter.limit("5/minute")  # Limit to 5 requests per minute per IP
def get_content_summary(
    request: SummaryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Request a summary of a specific chapter or section
    """
    from backend.src.ai.rag_service import RAGService
    from backend.src.services.chapter_service import ChapterService

    rag_service = RAGService()
    chapter_service = ChapterService()

    # Get the chapter content
    chapter = chapter_service.get_chapter_by_id(db, request.chapter_id)
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chapter with id {request.chapter_id} not found"
        )

    # Prepare the content for summarization
    content_to_summarize = chapter.content
    if request.section:
        # In a full implementation, we would extract the specific section
        # For now, we'll just use the chapter content
        pass

    # Generate summary using the RAG service
    summary = rag_service.generate_content_summary(
        content_to_summarize,
        detail_level=request.detail_level,
        user_id=str(current_user.id)
    )

    # Create an AI interaction record for the summary request
    from backend.src.models.ai_interaction import AIInteractionCreate, InteractionType
    from backend.src.services.ai_interaction_service import AIInteractionService
    from datetime import datetime

    interaction_service = AIInteractionService()
    interaction_data = AIInteractionCreate(
        user_id=str(current_user.id),
        chapter_id=request.chapter_id,
        query=f"Generate {request.detail_level} summary for section: {request.section or 'entire chapter'}",
        response=summary,
        interaction_type=InteractionType.summary,
        timestamp=datetime.now()
    )

    interaction_service.create_interaction(db, interaction_data)

    return {
        "summary": summary,
        "key_points": extract_key_points(summary),  # This would be a helper function
        "time_to_read": estimate_reading_time(summary)
    }

# Additional model for the summary request
from pydantic import BaseModel

class SummaryRequest(BaseModel):
    chapter_id: str
    section: str = None
    detail_level: str = "medium"  # Options: brief, medium, detailed

def extract_key_points(summary: str) -> list:
    """
    Extract key points from the summary (simplified implementation)
    """
    # In a real implementation, this would use NLP to extract key points
    sentences = summary.split('. ')
    # Just return the first few sentences as key points for demonstration
    return sentences[:3] if len(sentences) >= 3 else sentences

def estimate_reading_time(text: str) -> int:
    """
    Estimate reading time in minutes based on text length (simplified implementation)
    """
    words_per_minute = 200  # Average reading speed
    word_count = len(text.split())
    minutes = word_count / words_per_minute
    return round(minutes)

# AI Recommendation Feedback Endpoints
@router.post("/recommendation-feedback")
def submit_recommendation_feedback(
    feedback_data: AIRecommendationFeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Submit feedback on an AI recommendation
    """
    from backend.src.services.ai_recommendation_feedback_service import AIRecommendationFeedbackService

    service = AIRecommendationFeedbackService()
    feedback = service.submit_feedback(db, feedback_data, str(current_user.id))

    return feedback

@router.get("/recommendation-feedback/{recommendation_id}")
def get_recommendation_feedback(
    recommendation_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get feedback for a specific recommendation
    """
    from backend.src.services.ai_recommendation_feedback_service import AIRecommendationFeedbackService

    service = AIRecommendationFeedbackService()
    feedback_list = service.get_feedback_by_recommendation(db, recommendation_id, skip, limit)

    return feedback_list

@router.get("/recommendation-feedback/{recommendation_id}/aggregate")
def get_aggregated_recommendation_feedback(
    recommendation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get aggregated feedback for a specific recommendation
    """
    from backend.src.services.ai_recommendation_feedback_service import AIRecommendationFeedbackService

    service = AIRecommendationFeedbackService()
    aggregated_feedback = service.get_aggregated_feedback(db, recommendation_id)

    return aggregated_feedback

# We need to import the proper model from the models module
from backend.src.models.ai_recommendation_feedback import AIRecommendationFeedbackCreate