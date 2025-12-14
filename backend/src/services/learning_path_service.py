from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.src.models.ai_interaction import AIInteraction
from backend.src.models.learning_session import LearningSession
from backend.src.models.chapter import Chapter
from backend.src.models.content_module import ContentModule
from datetime import datetime, timedelta


class LearningPathService:
    """
    Service for managing personalized learning paths based on user progress
    """
    
    def __init__(self):
        # This could be configured with different algorithms
        self.default_weights = {
            'progress': 0.4,
            'time_spent': 0.2,
            'difficulty': 0.2,
            'interest': 0.2
        }
    
    def get_learning_path(self, db: Session, user_id: str) -> Dict[str, Any]:
        """
        Generate a personalized learning path for a user based on their progress and preferences
        """
        # Get user's learning sessions to understand their progress
        sessions = db.query(LearningSession).filter(
            LearningSession.user_id == user_id
        ).all()
        
        # Get user's AI interactions to understand their interests and difficulties
        interactions = db.query(AIInteraction).filter(
            AIInteraction.user_id == user_id
        ).order_by(AIInteraction.timestamp.desc()).limit(20).all()
        
        # Get all chapters to recommend from
        all_chapters = db.query(Chapter).filter(Chapter.is_published == True).all()
        all_modules = db.query(ContentModule).filter(ContentModule.is_published == True).all()
        
        # Calculate recommendations
        recommendations = self._calculate_recommendations(
            db, user_id, sessions, interactions, all_chapters
        )
        
        # Calculate progress summary
        progress_summary = self._calculate_progress_summary(db, user_id, sessions)
        
        return {
            "recommended_chapters": recommendations,
            "learning_goals": self._get_learning_goals(db, user_id),
            "progress_summary": progress_summary
        }
    
    def _calculate_recommendations(self, db: Session, user_id: str, sessions: List[LearningSession], 
                                 interactions: List[AIInteraction], all_chapters: List[Chapter]) -> List[Dict[str, Any]]:
        """
        Calculate chapter recommendations based on user behavior
        """
        # Create a score for each chapter based on various factors
        chapter_scores = {}
        
        # Initialize scores
        for chapter in all_chapters:
            chapter_scores[chapter.id] = {
                "chapter": chapter,
                "score": 0,
                "reasons": []
            }
        
        # Factor 1: Progress - chapters not started or not completed get higher priority
        completed_chapter_ids = [session.chapter_id for session in sessions if session.progress_percentage == 100]
        for chapter in all_chapters:
            if chapter.id not in completed_chapter_ids:
                chapter_scores[chapter.id]["score"] += 10
                chapter_scores[chapter.id]["reasons"].append("Not completed yet")
            else:
                chapter_scores[chapter.id]["score"] -= 5
                chapter_scores[chapter.id]["reasons"].append("Already completed")
        
        # Factor 2: Time spent - chapters where user spent significant time
        for session in sessions:
            if session.progress_percentage > 50:  # Only consider if they made progress
                time_score = min(session.progress_percentage / 10, 5)  # Max 5 points
                chapter_scores[session.chapter_id]["score"] += time_score
        
        # Factor 3: AI interactions - chapters related to questions asked
        for interaction in interactions:
            if interaction.chapter_id and interaction.chapter_id in chapter_scores:
                # If user asked questions about this chapter, they might be interested
                chapter_scores[interaction.chapter_id]["score"] += 7
                chapter_scores[interaction.chapter_id]["reasons"].append("Asked questions about this")
        
        # Sort chapters by score (highest first)
        sorted_chapters = sorted(
            chapter_scores.values(), 
            key=lambda x: x["score"], 
            reverse=True
        )
        
        # Format the results
        recommendations = []
        for item in sorted_chapters[:10]:  # Return top 10
            recommendations.append({
                "id": str(item["chapter"].id),
                "title": item["chapter"].title,
                "module_title": self._get_module_title(db, item["chapter"].module_id),
                "reason": ", ".join(item["reasons"]),
                "priority": self._get_priority_from_score(item["score"]),
                "estimated_reading_time": item["chapter"].estimated_reading_time
            })
        
        return recommendations
    
    def _get_module_title(self, db: Session, module_id: str) -> str:
        """
        Get module title by its ID
        """
        module = db.query(ContentModule).filter(ContentModule.id == module_id).first()
        return module.title if module else "Unknown Module"
    
    def _get_priority_from_score(self, score: float) -> str:
        """
        Convert score to priority level
        """
        if score >= 15:
            return "high"
        elif score >= 8:
            return "medium"
        else:
            return "low"
    
    def _calculate_progress_summary(self, db: Session, user_id: str, sessions: List[LearningSession]) -> Dict[str, Any]:
        """
        Calculate progress summary for the user
        """
        total_sessions = len(sessions)
        completed_sessions = len([s for s in sessions if s.progress_percentage == 100])
        in_progress_sessions = len([s for s in sessions if 0 < s.progress_percentage < 100])
        
        # Calculate overall progress percentage
        total_progress = sum(s.progress_percentage for s in sessions)
        avg_progress = total_progress / len(sessions) if sessions else 0
        
        # Get the last active chapter
        last_active = None
        if sessions:
            last_session = max(sessions, key=lambda s: s.updated_at)
            chapter = db.query(Chapter).filter(Chapter.id == last_session.chapter_id).first()
            if chapter:
                last_active = {
                    "chapter_id": str(chapter.id),
                    "chapter_title": chapter.title,
                    "module_id": str(chapter.module_id),
                    "progress": last_session.progress_percentage
                }
        
        return {
            "total_sessions": total_sessions,
            "completed_sessions": completed_sessions,
            "in_progress_sessions": in_progress_sessions,
            "average_progress": round(avg_progress, 2),
            "last_active_chapter": last_active,
            "estimated_completion_time": self._estimate_completion_time(db, user_id, sessions)
        }
    
    def _estimate_completion_time(self, db: Session, user_id: str, sessions: List[LearningSession]) -> str:
        """
        Estimate time to complete the textbook based on user's reading pace
        """
        # This is a simple estimation based on completed chapters and time spent
        # In a real implementation, this would be more sophisticated
        if not sessions:
            return "Not enough data to estimate"
        
        # Calculate average time per chapter based on completed sessions
        completed_sessions = [s for s in sessions if s.progress_percentage == 100]
        if not completed_sessions:
            return "Estimated based on average reading time"
        
        # This is a placeholder implementation
        return "Based on your pace, estimated 2-3 weeks remaining"
    
    def _get_learning_goals(self, db: Session, user_id: str) -> List[Dict[str, Any]]:
        """
        Get user's learning goals
        """
        # In a real implementation, this would come from user goals stored in database
        # For now, return some sample goals
        return [
            {
                "id": "goal-1",
                "title": "Complete Introduction to Robotics Module",
                "status": "in_progress",
                "target_date": (datetime.now() + timedelta(weeks=2)).strftime('%Y-%m-%d')
            },
            {
                "id": "goal-2", 
                "title": "Master Robot Control Systems",
                "status": "not_started",
                "target_date": (datetime.now() + timedelta(weeks=4)).strftime('%Y-%m-%d')
            }
        ]