from typing import Optional
from sqlalchemy.orm import Session
from backend.src.models.user import User, UserCreate, UserUpdate
from datetime import datetime


class UserService:
    """
    Service for managing users
    """
    
    def create_user(self, db: Session, user_data: dict) -> User:
        """
        Create a new user
        """
        user = User(**user_data)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    def get_user_by_id(self, db: Session, user_id: str) -> Optional[User]:
        """
        Retrieve a user by their ID
        """
        return db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """
        Retrieve a user by their email
        """
        return db.query(User).filter(User.email == email).first()
    
    def update_user(self, db: Session, user_id: str, user_update: UserUpdate) -> Optional[User]:
        """
        Update a user with new data
        """
        user = self.get_user_by_id(db, user_id)
        if user:
            for field, value in user_update.dict(exclude_unset=True).items():
                setattr(user, field, value)
            db.commit()
            db.refresh(user)
        return user
    
    def update_user_last_login(self, db: Session, user_id: str):
        """
        Update the last login time for a user
        """
        user = self.get_user_by_id(db, user_id)
        if user:
            user.last_login_at = datetime.utcnow()
            db.commit()
            db.refresh(user)
        return user
    
    def delete_user(self, db: Session, user_id: str) -> bool:
        """
        Delete a user by their ID
        """
        user = self.get_user_by_id(db, user_id)
        if user:
            db.delete(user)
            db.commit()
            return True
        return False