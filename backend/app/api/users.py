from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import hashlib

from ..database import get_db
from ..models import User
from ..schemas import UserLogin, UserPasswordChange

router = APIRouter(prefix="/users", tags=["users"])

# OPTIONS requests are now handled globally in main.py

def hash_password(password: str) -> str:
    """Hash a password using SHA-256 (in production, use bcrypt or similar)"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return hash_password(plain_password) == hashed_password

@router.get("/")
def get_users(db: Session = Depends(get_db)):
    """Get all active users (without sensitive information)"""
    users = db.query(User).filter(User.is_active == True).all()
    return [
        {
            "id": user.id,
            "username": user.username,
            "name": user.name,
            "email": user.email,
            "is_active": user.is_active
        }
        for user in users
    ]

@router.post("/login")
def login_user(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate a user"""
    # Find user by username
    db_user = db.query(User).filter(User.username == user_credentials.username).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Verify password
    if not verify_password(user_credentials.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Check if user is active
    if not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is deactivated"
        )
    
    # Return user info (without password)
    return {
        "id": db_user.id,
        "username": db_user.username,
        "name": db_user.name,
        "email": db_user.email,
        "is_active": db_user.is_active
    }

@router.put("/change-password")
def change_password(password_data: UserPasswordChange, db: Session = Depends(get_db)):
    """Change user password"""
    # Find user by username
    db_user = db.query(User).filter(User.username == password_data.username).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify current password
    if not verify_password(password_data.current_password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )
    
    # Update password
    hashed_new_password = hash_password(password_data.new_password)
    db_user.password = hashed_new_password
    
    db.commit()
    db.refresh(db_user)
    
    return {"message": "Password updated successfully"}
