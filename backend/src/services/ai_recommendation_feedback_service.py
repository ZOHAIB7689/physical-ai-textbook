from typing import List, Optional
from sqlalchemy.orm import Session
from backend.src.models.ai_recommendation_feedback import AIRecommendationFeedback, AIRecommendationFeedbackCreate, AIRecommendationFeedbackUpdate


class AIRecommendationFeedbackService:
    """
    Service for managing feedback on AI recommendations
    """
    
    def submit_feedback(self, db: Session, feedback_data: AIRecommendationFeedbackCreate, user_id: str) -> AIRecommendationFeedback:
        """
        Submit feedback on an AI recommendation
        """
        feedback = AIRecommendationFeedback(
            user_id=user_id,
            recommendation_id=feedback_data.recommendation_id,
            feedback_type=feedback_data.feedback_type,
            comment=feedback_data.comment,
            rating=feedback_data.rating,
            source_interaction_id=feedback_data.source_interaction_id
        )
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        return feedback
    
    def get_feedback_by_user(self, db: Session, user_id: str, skip: int = 0, limit: int = 100) -> List[AIRecommendationFeedback]:
        """
        Get all feedback submitted by a user
        """
        return db.query(AIRecommendationFeedback).filter(
            AIRecommendationFeedback.user_id == user_id
        ).offset(skip).limit(limit).all()
    
    def get_feedback_by_recommendation(self, db: Session, recommendation_id: str, skip: int = 0, limit: int = 100) -> List[AIRecommendationFeedback]:
        """
        Get all feedback for a specific recommendation
        """
        return db.query(AIRecommendationFeedback).filter(
            AIRecommendationFeedback.recommendation_id == recommendation_id
        ).offset(skip).limit(limit).all()
    
    def get_feedback_by_type(self, db: Session, feedback_type: str, skip: int = 0, limit: int = 100) -> List[AIRecommendationFeedback]:
        """
        Get feedback of a specific type
        """
        return db.query(AIRecommendationFeedback).filter(
            AIRecommendationFeedback.feedback_type == feedback_type
        ).offset(skip).limit(limit).all()
    
    def get_aggregated_feedback(self, db: Session, recommendation_id: str) -> dict:
        """
        Get aggregated feedback statistics for a recommendation
        """
        feedback_list = self.get_feedback_by_recommendation(db, recommendation_id, 0, 1000)
        
        if not feedback_list:
            return {
                "recommendation_id": recommendation_id,
                "total_feedback": 0,
                "like_count": 0,
                "dislike_count": 0,
                "helpful_count": 0,
                "not_helpful_count": 0,
                "average_rating": None,
                "positive_ratio": 0.0
            }
        
        # Count different feedback types
        feedback_counts = {
            "like": 0,
            "dislike": 0,
            "helpful": 0,
            "not_helpful": 0,
            "report_inaccurate": 0,
            "suggest_improvement": 0
        }
        
        ratings = []
        
        for feedback in feedback_list:
            if feedback.feedback_type in feedback_counts:
                feedback_counts[feedback.feedback_type] += 1
            
            if feedback.rating is not None:
                ratings.append(feedback.rating)
        
        avg_rating = sum(ratings) / len(ratings) if ratings else None
        
        return {
            "recommendation_id": recommendation_id,
            "total_feedback": len(feedback_list),
            "like_count": feedback_counts["like"],
            "dislike_count": feedback_counts["dislike"],
            "helpful_count": feedback_counts["helpful"],
            "not_helpful_count": feedback_counts["not_helpful"],
            "report_inaccurate_count": feedback_counts["report_inaccurate"],
            "suggest_improvement_count": feedback_counts["suggest_improvement"],
            "average_rating": avg_rating,
            "positive_ratio": (feedback_counts["helpful"] + feedback_counts["like"]) / len(feedback_list)
        }
    
    def update_feedback(self, db: Session, feedback_id: str, user_id: str, feedback_update: AIRecommendationFeedbackUpdate) -> Optional[AIRecommendationFeedback]:
        """
        Update existing feedback (only allow updating by the original submitter)
        """
        feedback = self.get_feedback_by_id(db, feedback_id)
        if feedback and feedback.user_id == user_id:
            for field, value in feedback_update.dict(exclude_unset=True).items():
                setattr(feedback, field, value)
            db.commit()
            db.refresh(feedback)
            return feedback
        return None
    
    def delete_feedback(self, db: Session, feedback_id: str, user_id: str) -> bool:
        """
        Delete feedback (only allow deleting by the original submitter)
        """
        feedback = self.get_feedback_by_id(db, feedback_id)
        if feedback and feedback.user_id == user_id:
            db.delete(feedback)
            db.commit()
            return True
        return False
    
    def get_feedback_by_id(self, db: Session, feedback_id: str) -> Optional[AIRecommendationFeedback]:
        """
        Get feedback by its ID
        """
        return db.query(AIRecommendationFeedback).filter(
            AIRecommendationFeedback.id == feedback_id
        ).first()