from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.src.services.learning_path_service import LearningPathService
from backend.src.services.chapter_service import ChapterService
from backend.src.services.learning_session_service import LearningSessionService
from backend.src.ai.learning_agent import LearningAgent
from backend.src.models.chapter import Chapter
from backend.src.models.learning_session import LearningSession


class AdaptiveContentService:
    """
    Service for delivering adaptive content based on AI recommendations and user behavior
    """
    
    def __init__(self):
        self.learning_path_service = LearningPathService()
        self.chapter_service = ChapterService()
        self.learning_session_service = LearningSessionService()
        self.learning_agent = LearningAgent()
    
    def get_adaptive_content_sequence(self, db: Session, user_id: str, current_chapter_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get the next recommended content pieces based on user's progress and learning patterns
        """
        # Get the user's learning path
        learning_path = self.learning_path_service.get_learning_path(db, user_id)
        
        # Get user analysis to understand their learning patterns
        user_analysis = self.learning_agent.analyze_user_progress(db, user_id)
        
        # Adjust the recommendations based on user analysis
        recommendations = self._adjust_recommendations_for_user(
            db, user_id, learning_path["recommended_chapters"], user_analysis
        )
        
        # Format the adaptive content sequence
        content_sequence = []
        
        # Add current chapter if provided
        if current_chapter_id:
            current_chapter = self.chapter_service.get_chapter_by_id(db, current_chapter_id)
            if current_chapter:
                content_sequence.append({
                    "id": str(current_chapter.id),
                    "title": current_chapter.title,
                    "type": "current",
                    "estimated_reading_time": current_chapter.estimated_reading_time,
                    "priority": "current"
                })
        
        # Add recommended chapters
        for rec in recommendations:
            chapter = self.chapter_service.get_chapter_by_id(db, rec["id"])
            if chapter:
                content_sequence.append({
                    "id": str(chapter.id),
                    "title": chapter.title,
                    "module_title": self._get_module_title(db, chapter.module_id),
                    "type": "recommended",
                    "reason": rec.get("reason", "AI recommendation based on your progress"),
                    "priority": rec.get("priority", "medium"),
                    "estimated_reading_time": chapter.estimated_reading_time
                })
        
        return content_sequence[:10]  # Limit to top 10 recommendations
    
    def _adjust_recommendations_for_user(self, db: Session, user_id: str, recommendations: List[Dict], user_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Adjust recommendations based on user's learning analysis
        """
        adjusted_recs = []
        
        for rec in recommendations:
            # Adjust priority based on user's learning style
            if user_analysis.get("learning_style") == "hands_on":
                # Boost practical chapters
                if "implementation" in rec["title"].lower() or "example" in rec["title"].lower():
                    rec["priority"] = "high"
            elif user_analysis.get("learning_style") == "theoretical":
                # Boost concept-heavy chapters
                if "theory" in rec["title"].lower() or "principle" in rec["title"].lower():
                    rec["priority"] = "high"
            
            # Address weaknesses
            for weakness in user_analysis.get("weaknesses", []):
                if weakness.get("chapter", {}).get("title", "").lower() in rec["title"].lower():
                    rec["priority"] = "high"
                    rec["reason"] = "Addressing identified weakness area"
            
            # Adjust based on engagement level
            if user_analysis.get("engagement_level") == "low":
                # Suggest easier content to build confidence
                if rec["priority"] == "high":
                    # Maybe add a foundational chapter first
                    pass
            
            adjusted_recs.append(rec)
        
        # Re-sort based on adjusted priorities
        priority_map = {"high": 3, "medium": 2, "low": 1}
        adjusted_recs.sort(key=lambda x: priority_map.get(x.get("priority", "medium"), 0), reverse=True)
        
        return adjusted_recs
    
    def get_alternative_content(self, db: Session, user_id: str, difficulty: str = "easier") -> List[Dict[str, Any]]:
        """
        Get alternative content when user is struggling with current material
        """
        # Get user's recent learning sessions to identify problematic areas
        recent_sessions = db.query(LearningSession).filter(
            LearningSession.user_id == user_id
        ).order_by(LearningSession.updated_at.desc()).limit(5).all()
        
        alternative_content = []
        
        for session in recent_sessions:
            if session.progress_percentage < 50:  # User is struggling with this chapter
                chapter = self.chapter_service.get_chapter_by_id(db, session.chapter_id)
                if chapter:
                    # Find related foundational content
                    related_content = self._find_foundational_content(db, chapter)
                    for content in related_content:
                        alternative_content.append({
                            "id": str(content.id),
                            "title": content.title,
                            "type": "foundational",
                            "reason": f"Preparatory content for '{chapter.title}'",
                            "estimated_reading_time": content.estimated_reading_time
                        })
        
        return alternative_content
    
    def _find_foundational_content(self, db: Session, chapter: Chapter) -> List[Chapter]:
        """
        Find foundational content related to the given chapter
        """
        # In a real implementation, this would use content relationships or embeddings
        # to find conceptually related foundational material
        
        # For now, return some sample foundational content
        # In a real system, this would analyze the content to find prerequisite concepts
        foundational_chapters = db.query(Chapter).filter(
            Chapter.module_id == chapter.module_id,
            Chapter.chapter_number < chapter.chapter_number  # Earlier chapters in the same module
        ).limit(3).all()
        
        return foundational_chapters
    
    def _get_module_title(self, db: Session, module_id: str) -> str:
        """
        Get module title by its ID
        """
        from backend.src.models.content_module import ContentModule
        module = db.query(ContentModule).filter(ContentModule.id == module_id).first()
        return module.title if module else "Unknown Module"
    
    def get_personalized_practice_problems(self, db: Session, user_id: str, chapter_id: str) -> List[Dict[str, Any]]:
        """
        Generate personalized practice problems based on chapter content and user weaknesses
        """
        # Get user analysis
        user_analysis = self.learning_agent.analyze_user_progress(db, user_id)
        
        # In a real implementation, this would generate practice problems based on:
        # 1. The chapter content
        # 2. User's weaknesses
        # 3. User's learning style
        
        # For now, return sample practice problems
        practice_problems = [
            {
                "id": "prob-1",
                "question": f"Based on {chapter_id}, explain the key concepts you learned.",
                "type": "reflection",
                "difficulty": "low"
            },
            {
                "id": "prob-2", 
                "question": f"How would you apply the concepts from {chapter_id} in a practical situation?",
                "type": "application",
                "difficulty": "medium"
            }
        ]
        
        # Add problems targeting user's weaknesses
        for weakness in user_analysis.get("weaknesses", [])[:2]:
            practice_problems.append({
                "id": f"prob-weak-{len(practice_problems)}",
                "question": f"Explain {weakness.get('topic', 'this concept')} in your own words.",
                "type": "understanding",
                "difficulty": "medium"
            })
        
        return practice_problems