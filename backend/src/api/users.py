from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.src.database.database import get_db
from backend.src.models.user import UserCreate, UserResponse, UserUpdate
from backend.src.services.user_service import UserService
from backend.src.auth.auth import get_current_active_user, authenticate_user, create_access_token, get_password_hash
from backend.src.models.user import User
from datetime import timedelta
import os

router = APIRouter()
service = UserService()

@router.post("/register", response_model=UserResponse)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user
    """
    # Check if user already exists
    existing_user = service.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists"
        )
    
    # Hash the password
    hashed_password = get_password_hash(user_data.password)
    
    # Create user with hashed password
    user_data_dict = user_data.dict()
    user_data_dict["password_hash"] = hashed_password
    del user_data_dict["password"]  # Remove plain password
    
    user = service.create_user(db, user_data_dict)
    return user


@router.post("/login")
def login_user(
    email: str,
    password: str,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return access token
    """
    user = authenticate_user(db, email, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login time
    service.update_user_last_login(db, user.id)
    
    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(user)
    }


@router.get("/profile", response_model=UserResponse)
def get_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get authenticated user's profile information
    """
    return current_user


@router.put("/profile", response_model=UserResponse)
def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update authenticated user's profile information
    """
    updated_user = service.update_user(db, current_user.id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return updated_user