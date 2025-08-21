#!/usr/bin/env python3
"""
Script to initialize the database with default users
Run this after creating the users table
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine
from app.models import User, Base
import hashlib

def hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_users():
    """Initialize the database with default users"""
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if users already exist
        existing_users = db.query(User).count()
        if existing_users > 0:
            print(f"Database already has {existing_users} users. Skipping initialization.")
            return
        
        # Create default users
        default_users = [
            {
                "username": "bob",
                "name": "Bob",
                "email": "bob@example.com",
                "password": "Pass@1234"
            },
            {
                "username": "leah",
                "name": "Leah",
                "email": "leah@example.com",
                "password": "Pass@1234"
            },
            {
                "username": "matthew",
                "name": "Matthew",
                "email": "matthew@example.com",
                "password": "Pass@1234"
            }
        ]
        
        for user_data in default_users:
            # Hash the password
            hashed_password = hash_password(user_data["password"])
            
            # Create user object
            user = User(
                username=user_data["username"],
                name=user_data["name"],
                email=user_data["email"],
                password=hashed_password,
                is_active=True
            )
            
            db.add(user)
            print(f"Created user: {user_data['username']}")
        
        # Commit all users
        db.commit()
        print("Successfully initialized database with default users!")
        
    except Exception as e:
        print(f"Error initializing users: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Initializing database with default users...")
    init_users()
