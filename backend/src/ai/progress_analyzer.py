from typing import List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from backend.src.models.learning_session import LearningSession
from backend.src.models.ai_interaction import AIInteraction
from backend.src.models.chapter import Chapter
from backend.src.models.content_module import ContentModule


class ProgressAnalyzer:
    """
    Analyzes user's progress to identify patterns, strengths, weaknesses, and learning trends
    """
    
    def __init__(self):
        self.time_threshold = 30  # minutes considered a significant read time
        self.engagement_threshold = 75  # progress percentage for high engagement
    
    def analyze_user_progress(self, db: Session, user_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Analyze user's learning progress over the specified number of days
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Get user's learning sessions within the time frame
        sessions = db.query(LearningSession).filter(
            LearningSession.user_id == user_id,
            LearningSession.created_at >= cutoff_date
        ).all()
        
        # Get user's AI interactions within the time frame
        interactions = db.query(AIInteraction).filter(
            AIInteraction.user_id == user_id,
            AIInteraction.timestamp >= cutoff_date
        ).order_by(AIInteraction.timestamp.desc()).all()
        
        # Calculate progress metrics
        progress_metrics = self._calculate_progress_metrics(db, sessions)
        
        # Analyze engagement patterns
        engagement_analysis = self._analyze_engagement_patterns(db, sessions)
        
        # Identify strengths and weaknesses
        strengths_weaknesses = self._identify_strengths_and_weaknesses(db, user_id, interactions)
        
        # Calculate learning pace
        learning_pace = self._calculate_learning_pace(sessions)
        
        # Generate trend analysis
        trends = self._analyze_learning_trends(sessions, interactions)
        
        return {
            "time_frame": f"Last {days} days",
            "progress_metrics": progress_metrics,
            "engagement_analysis": engagement_analysis,
            "strengths": strengths_weaknesses["strengths"],
            "weaknesses": strengths_weaknesses["weaknesses"],
            "learning_pace": learning_pace,
            "trends": trends
        }
    
    def _calculate_progress_metrics(self, db: Session, sessions: List[LearningSession]) -> Dict[str, Any]:
        """
        Calculate basic progress metrics like completion rate, average progress, etc.
        """
        if not sessions:
            return {
                "total_sessions": 0,
                "completed_sessions": 0,
                "incomplete_sessions": 0,
                "average_progress": 0,
                "completion_rate": 0
            }
        
        total_sessions = len(sessions)
        completed_sessions = len([s for s in sessions if s.progress_percentage == 100])
        incomplete_sessions = total_sessions - completed_sessions
        
        total_progress = sum(s.progress_percentage for s in sessions)
        average_progress = total_progress / total_sessions
        
        completion_rate = (completed_sessions / total_sessions) * 100 if total_sessions > 0 else 0
        
        return {
            "total_sessions": total_sessions,
            "completed_sessions": completed_sessions,
            "incomplete_sessions": incomplete_sessions,
            "average_progress": round(average_progress, 2),
            "completion_rate": round(completion_rate, 2)
        }
    
    def _analyze_engagement_patterns(self, db: Session, sessions: List[LearningSession]) -> Dict[str, Any]:
        """
        Analyze engagement patterns like time spent, progress made, etc.
        """
        if not sessions:
            return {"engagement_level": "none", "avg_time_per_session": 0, "most_engaging_chapters": []}
        
        # Calculate engagement metrics
        high_engagement_sessions = [s for s in sessions if s.progress_percentage >= self.engagement_threshold]
        avg_progress = sum(s.progress_percentage for s in sessions) / len(sessions)
        
        # Get most engaging chapters (those with high progress and time spent)
        most_engaging = sorted(
            sessions, 
            key=lambda s: s.progress_percentage, 
            reverse=True
        )[:5]  # Top 5
        
        # Format the most engaging chapters
        engaging_chapters = []
        for session in most_engaging:
            chapter = db.query(Chapter).filter(Chapter.id == session.chapter_id).first()
            if chapter:
                engaging_chapters.append({
                    "chapter_id": str(chapter.id),
                    "title": chapter.title,
                    "progress": session.progress_percentage,
                    "module": self._get_module_title(db, chapter.module_id)
                })
        
        # Determine engagement level
        engagement_level = "low"
        if avg_progress >= 80:
            engagement_level = "high"
        elif avg_progress >= 50:
            engagement_level = "medium"
        
        return {
            "engagement_level": engagement_level,
            "average_progress": round(avg_progress, 2),
            "high_engagement_sessions_count": len(high_engagement_sessions),
            "most_engaging_chapters": engaging_chapters
        }
    
    def _identify_strengths_and_weaknesses(self, db: Session, user_id: str, interactions: List[AIInteraction]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Identify strengths and weaknesses based on AI interactions
        """
        strengths = []
        weaknesses = []
        
        # Analyze patterns in AI interactions
        for interaction in interactions:
            query_lower = interaction.query.lower()
            
            # Identify potential weaknesses based on question types
            if any(word in query_lower for word in ["don't understand", "confused", "help", "struggling", "difficult"]):
                weaknesses.append({
                    "topic": interaction.query[:100] + "..." if len(interaction.query) > 100 else interaction.query,
                    "timestamp": interaction.timestamp,
                    "chapter": self._get_chapter_info(db, interaction.chapter_id)
                })
            
            # For strengths, we might look for positive engagement indicators
            # For now, we'll just return the data structure
            if any(word in query_lower for word in ["understand", "clear", "mastered", "got it"]):
                strengths.append({
                    "topic": interaction.query[:100] + "..." if len(interaction.query) > 100 else interaction.query,
                    "timestamp": interaction.timestamp,
                    "chapter": self._get_chapter_info(db, interaction.chapter_id)
                })
        
        return {
            "strengths": strengths[:5],  # Return top 5
            "weaknesses": weaknesses[:5]  # Return top 5
        }
    
    def _calculate_learning_pace(self, sessions: List[LearningSession]) -> Dict[str, Any]:
        """
        Calculate the user's learning pace
        """
        if len(sessions) < 2:
            return {"pace": "insufficient_data", "chapters_per_day": 0}
        
        # Calculate the date range
        start_date = min(s.created_at.date() for s in sessions)
        end_date = max(s.created_at.date() for s in sessions)
        
        # Calculate days between first and last session
        days_diff = (end_date - start_date).days + 1  # +1 to include both start and end days
        
        # Calculate chapters per day
        chapters_per_day = len(set(s.chapter_id for s in sessions)) / days_diff if days_diff > 0 else 0
        
        pace_description = "slow"
        if chapters_per_day >= 1.0:
            pace_description = "fast"
        elif chapters_per_day >= 0.5:
            pace_description = "moderate"
        
        return {
            "pace": pace_description,
            "chapters_per_day": round(chapters_per_day, 2),
            "days_of_activity": days_diff
        }
    
    def _analyze_learning_trends(self, sessions: List[LearningSession], interactions: List[AIInteraction]) -> List[Dict[str, Any]]:
        """
        Analyze trends in learning behavior
        """
        trends = []
        
        if sessions:
            # Check for consistency (regular study vs sporadic)
            dates_active = set(s.created_at.date() for s in sessions)
            days_between_sessions = []
            sorted_sessions = sorted(sessions, key=lambda s: s.created_at)
            
            for i in range(1, len(sorted_sessions)):
                diff = (sorted_sessions[i].created_at.date() - sorted_sessions[i-1].created_at.date()).days
                days_between_sessions.append(diff)
            
            if days_between_sessions:
                avg_gap = sum(days_between_sessions) / len(days_between_sessions)
                
                if avg_gap > 3:
                    trends.append({
                        "type": "consistency",
                        "description": "Study sessions are sporadic",
                        "suggestion": "Try to study more regularly"
                    })
                else:
                    trends.append({
                        "type": "consistency", 
                        "description": "Study sessions are consistent",
                        "suggestion": "Great consistency in your studying"
                    })
        
        # Check for interaction patterns
        if interactions:
            recent_interactions = [i for i in interactions if i.timestamp >= datetime.now() - timedelta(days=7)]
            if len(recent_interactions) > 5:  # Active in the last week
                trends.append({
                    "type": "activity",
                    "description": "High recent activity",
                    "suggestion": "You're actively engaging with the material"
                })
            else:
                trends.append({
                    "type": "activity",
                    "description": "Low recent activity",
                    "suggestion": "Try to spend more time on the material"
                })
        
        return trends
    
    def _get_chapter_info(self, db: Session, chapter_id: str) -> Dict[str, str]:
        """
        Get chapter information by ID
        """
        if not chapter_id:
            return {"title": "General", "module": "N/A"}
        
        chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
        if chapter:
            return {
                "title": chapter.title,
                "module": self._get_module_title(db, chapter.module_id)
            }
        return {"title": "Unknown", "module": "N/A"}
    
    def _get_module_title(self, db: Session, module_id: str) -> str:
        """
        Get module title by its ID
        """
        module = db.query(ContentModule).filter(ContentModule.id == module_id).first()
        return module.title if module else "Unknown Module"