from typing import List, Optional
from sqlalchemy.orm import Session
from backend.src.models.learning_goal import LearningGoal, LearningGoalCreate, LearningGoalUpdate, GoalStatus
from datetime import datetime


class LearningGoalService:
    """
    Service for managing learning goals
    """
    
    def create_goal(self, db: Session, goal_data: LearningGoalCreate, user_id: str) -> LearningGoal:
        """
        Create a new learning goal
        """
        goal = LearningGoal(
            user_id=user_id,
            title=goal_data.title,
            description=goal_data.description,
            target_date=goal_data.target_date,
            progress_percentage=goal_data.progress_percentage
        )
        db.add(goal)
        db.commit()
        db.refresh(goal)
        return goal
    
    def get_goal_by_id(self, db: Session, goal_id: str) -> Optional[LearningGoal]:
        """
        Retrieve a learning goal by its ID
        """
        return db.query(LearningGoal).filter(LearningGoal.id == goal_id).first()
    
    def get_goals_by_user(self, db: Session, user_id: str, skip: int = 0, limit: int = 100) -> List[LearningGoal]:
        """
        Retrieve all learning goals for a specific user
        """
        return db.query(LearningGoal).filter(LearningGoal.user_id == user_id).offset(skip).limit(limit).all()
    
    def get_goals_by_status(self, db: Session, user_id: str, status: GoalStatus, skip: int = 0, limit: int = 100) -> List[LearningGoal]:
        """
        Retrieve all learning goals for a specific user with a specific status
        """
        return db.query(LearningGoal).filter(
            LearningGoal.user_id == user_id,
            LearningGoal.status == status
        ).offset(skip).limit(limit).all()
    
    def update_goal(self, db: Session, goal_id: str, goal_data: LearningGoalUpdate) -> Optional[LearningGoal]:
        """
        Update a learning goal with new data
        """
        goal = self.get_goal_by_id(db, goal_id)
        if goal:
            for field, value in goal_data.dict(exclude_unset=True).items():
                setattr(goal, field, value)
            
            # Update completed_at if status changes to completed
            if hasattr(goal_data, 'status') and goal_data.status == GoalStatus.completed and goal.status != GoalStatus.completed:
                goal.completed_at = datetime.now()
            elif hasattr(goal_data, 'status') and goal_data.status != GoalStatus.completed and goal.status == GoalStatus.completed:
                goal.completed_at = None  # Clear completion time if status changes from completed
                
            db.commit()
            db.refresh(goal)
        return goal
    
    def delete_goal(self, db: Session, goal_id: str) -> bool:
        """
        Delete a learning goal by its ID
        """
        goal = self.get_goal_by_id(db, goal_id)
        if goal:
            db.delete(goal)
            db.commit()
            return True
        return False
    
    def update_goal_progress(self, db: Session, goal_id: str, progress: int) -> Optional[LearningGoal]:
        """
        Update the progress of a learning goal
        """
        goal = self.get_goal_by_id(db, goal_id)
        if goal:
            goal.progress_percentage = min(100, max(0, progress))  # Ensure progress is between 0-100
            
            # Update status based on progress
            if progress >= 100 and goal.status != GoalStatus.completed:
                goal.status = GoalStatus.completed
                goal.completed_at = datetime.now()
            elif progress > 0 and progress < 100 and goal.status == GoalStatus.not_started:
                goal.status = GoalStatus.in_progress
            elif progress == 0 and goal.status != GoalStatus.on_hold:
                goal.status = GoalStatus.not_started
            
            db.commit()
            db.refresh(goal)
        return goal
    
    def set_goal_status(self, db: Session, goal_id: str, status: GoalStatus) -> Optional[LearningGoal]:
        """
        Set the status of a learning goal
        """
        goal = self.get_goal_by_id(db, goal_id)
        if goal:
            goal.status = status
            
            # Update completed_at if status changes to completed
            if status == GoalStatus.completed:
                goal.completed_at = datetime.now()
            elif status != GoalStatus.completed:
                goal.completed_at = None  # Clear completion time if no longer completed
                
            db.commit()
            db.refresh(goal)
        return goal