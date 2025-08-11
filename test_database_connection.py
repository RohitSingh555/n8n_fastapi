#!/usr/bin/env python3
"""
Quick test script to verify database connection
"""
import os
import sys
from dotenv import load_dotenv

# Add the backend directory to Python path
sys.path.append('./backend')

load_dotenv()

try:
    from app.database_utils import wait_for_database, ensure_database_exists
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL", "mysql+pymysql://n8n_user:n8n_password@localhost:3306/n8n_feedback")
    
    print(f"Testing database connection to: {database_url}")
    print("=" * 50)
    
    # Test database readiness
    if wait_for_database(database_url):
        print("✅ Database is ready!")
        
        # Test database existence
        if ensure_database_exists(database_url):
            print("✅ Database exists and is accessible!")
        else:
            print("❌ Database existence check failed")
    else:
        print("❌ Database is not ready")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the project root directory")
except Exception as e:
    print(f"❌ Error: {e}")
