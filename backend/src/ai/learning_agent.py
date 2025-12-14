from typing import List, Dict, Any
from backend.src.services.learning_path_service import LearningPathService
from backend.src.services.ai_interaction_service import AIInteractionService
from backend.src.services.chapter_service import ChapterService
from backend.src.services.learning_session_service import LearningSessionService
from backend.src.models.ai_interaction import InteractionType
from sqlalchemy.orm import Session
from datetime import datetime, timedelta


class LearningAgent:
    """
    AI agent that provides personalized learning recommendations and adjusts learning paths
    """
    
    def __init__(self):
        self.learning_path_service = LearningPathService()
        self.ai_interaction_service = AIInteractionService()
        self.chapter_service = ChapterService()
        self.learning_session_service = LearningSessionService()
        
        # Thresholds for different recommendations
        self.difficulty_threshold = 0.7  # If confidence is below this, suggest review
        self.engagement_threshold = 0.3  # If engagement is below this, suggest easier content
    
    def analyze_user_progress(self, db: Session, user_id: str) -> Dict[str, Any]:
        """
        Analyze user's progress to identify strengths, weaknesses, and learning patterns
        """
        # Get user's learning path and progress summary
        learning_path = self.learning_path_service.get_learning_path(db, user_id)
        progress_summary = learning_path["progress_summary"]
        
        # Get recent AI interactions to understand difficulties
        recent_interactions = db.query(
            AIInteraction
        ).filter(
            AIInteraction.user_id == user_id,
            AIInteraction.timestamp > datetime.now() - timedelta(days=7)
        ).order_by(AIInteraction.timestamp.desc()).limit(20).all()
        
        # Analyze patterns in interactions
        analysis = {
            "strengths": [],
            "weaknesses": [],
            "suggestions": [],
            "learning_style": self._infer_learning_style(db, user_id, recent_interactions),
            "engagement_level": self._calculate_engagement_level(progress_summary, recent_interactions)
        }
        
        # Identify strengths and weaknesses
        for interaction in recent_interactions:
            if "error" in interaction.query.lower() or "don't understand" in interaction.query.lower():
                analysis["weaknesses"].append({
                    "topic": interaction.query[:50] + "..." if len(interaction.query) > 50 else interaction.query,
                    "chapter_id": interaction.chapter_id,
                    "timestamp": interaction.timestamp
                })
        
        return analysis
    
    def _infer_learning_style(self, db: Session, user_id: str, interactions: List) -> str:
        """
        Infer learning style based on interaction patterns
        """
        # Simple heuristic-based approach
        question_count = len(interactions)
        
        if question_count == 0:
            return "exploratory"
        
        # Count different types of questions
        concept_questions = sum(1 for i in interactions if any(word in i.query.lower() for word in ["what is", "explain", "define", "meaning"]))
        application_questions = sum(1 for i in interactions if any(word in i.query.lower() for word in ["how to", "example", "apply", "practice"]))
        review_questions = sum(1 for i in interactions if any(word in i.query.lower() for word in ["review", "summary", "recap", "remind"]))
        
        if application_questions > concept_questions and application_questions > review_questions:
            return "hands_on"
        elif concept_questions > application_questions and concept_questions > review_questions:
            return "theoretical"
        else:
            return "balanced"
    
    def _calculate_engagement_level(self, progress_summary: Dict, interactions: List) -> str:
        """
        Calculate engagement level based on progress and interaction frequency
        """
        avg_progress = progress_summary.get("average_progress", 0)
        interaction_count = len(interactions)
        
        if avg_progress >= 80 and interaction_count >= 5:
            return "high"
        elif avg_progress >= 50 and interaction_count >= 2:
            return "medium"
        else:
            return "low"
    
    def generate_recommendations(self, db: Session, user_id: str) -> List[Dict[str, Any]]:
        """
        Generate personalized learning recommendations based on analysis
        """
        # Get user analysis
        analysis = self.analyze_user_progress(db, user_id)
        
        # Get learning path
        learning_path = self.learning_path_service.get_learning_path(db, user_id)
        recommendations = learning_path["recommended_chapters"]
        
        # Adjust recommendations based on analysis
        adjusted_recommendations = []
        
        for rec in recommendations:
            adjusted_rec = rec.copy()
            
            # Adjust priority based on user's learning style and engagement
            if analysis["learning_style"] == "hands_on":
                # If user prefers hands-on learning, prioritize chapters with practical examples
                if "implementation" in rec["title"].lower() or "example" in rec["title"].lower():
                    adjusted_rec["priority"] = "high"
                    adjusted_rec["reasons"] = [rec.get("reason", "") + " - matches hands-on learning style"]
            
            adjusted_recommendations.append(adjusted_rec)
        
        # Add specific recommendations based on weaknesses
        for weakness in analysis["weaknesses"][:3]:  # Add top 3 weaknesses
            if weakness["chapter_id"]:
                chapter = self.chapter_service.get_chapter_by_id(db, weakness["chapter_id"])
                if chapter:
                    adjusted_recommendations.append({
                        "id": weakness["chapter_id"],
                        "title": chapter.title,
                        "module_title": self._get_module_title(db, chapter.module_id),
                        "reason": "Addressing identified difficulty area",
                        "priority": "high",
                        "estimated_reading_time": chapter.estimated_reading_time
                    })
        
        return adjusted_recommendations
    
    def _get_module_title(self, db: Session, module_id: str) -> str:
        """
        Get module title by its ID
        """
        from backend.src.models.content_module import ContentModule
        module = db.query(ContentModule).filter(ContentModule.id == module_id).first()
        return module.title if module else "Unknown Module"
    
    def provide_adaptive_response(self, db: Session, user_id: str, query: str) -> str:
        """
        Provide adaptive response based on user's learning progress and preferences
        """
        # Analyze the user's profile and context
        analysis = self.analyze_user_progress(db, user_id)
        
        # Generate adaptive response based on learning style
        if analysis["learning_style"] == "theoretical":
            response = f"Based on your theoretical learning style, I'll provide the concept behind '{query}'. "
        elif analysis["learning_style"] == "hands_on":
            response = f"Based on your hands-on learning style, here's a practical example of '{query}'. "
        else:
            response = f"I'll explain '{query}' with a balanced approach. "
        
        # Add personalization based on engagement level
        if analysis["engagement_level"] == "low":
            response += "I notice you might need more engaging content. This topic is particularly interesting because... "
        elif analysis["engagement_level"] == "high":
            response += "Great question! This concept is particularly important for advanced learners like yourself. "
        
        # In a real implementation, we would call the RAG service here to get the actual answer
        response += f"Regarding '{query}', here's a detailed explanation based on the textbook content..."
        
        return response