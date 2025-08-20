from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Body, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import List, Optional
import uuid
import logging
import traceback
from datetime import datetime
import httpx
import os
import asyncio
import json

from . import models, schemas
from .database import engine, get_db, DATABASE_URL, recreate_engine
from .database_utils import wait_for_database, ensure_database_exists
from sqlalchemy import text
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def log_escape_characters(data: dict, operation: str):
    """Log information about escape characters in the data for debugging"""
    escape_patterns = {
        'newlines': r'\\n',
        'tabs': r'\\t',
        'carriage_returns': r'\\r',
        'backspaces': r'\\b',
        'form_feeds': r'\\f',
        'quotes': r'\\"',
        'backslashes': r'\\\\',
        'unicode': r'\\u[0-9a-fA-F]{4}'
    }
    
    for field_name, field_value in data.items():
        if isinstance(field_value, str) and field_value:
            found_escapes = []
            for escape_name, pattern in escape_patterns.items():
                if re.search(pattern, field_value):
                    count = len(re.findall(pattern, field_value))
                    found_escapes.append(f"{escape_name}: {count}")
            
            if found_escapes:
                logger.info(f"{operation} - Field '{field_name}' contains escape characters: {', '.join(found_escapes)}")
                logger.debug(f"{operation} - Field '{field_name}' value: {repr(field_value)}")

def validate_and_log_json_content(content: str, field_name: str) -> str:
    """Validate and log JSON content, handling escape characters gracefully"""
    if not content:
        return content
    
    # Clean the content by replacing problematic characters
    cleaned_content = content
    if "'" in content:
        # Replace unescaped apostrophes with escaped ones for JSON compatibility
        cleaned_content = content.replace("'", "\\'")
        logger.info(f"Cleaned {field_name}: replaced unescaped apostrophes with escaped ones")
    
    # Count escape sequences for logging
    escape_counts = {
        'newlines': cleaned_content.count('\\n'),
        'tabs': cleaned_content.count('\\t'),
        'carriage_returns': cleaned_content.count('\\r'),
        'backspaces': cleaned_content.count('\\b'),
        'form_feeds': cleaned_content.count('\\f'),
        'quotes': cleaned_content.count('\\"'),
        'backslashes': cleaned_content.count('\\\\'),
        'unicode': len(re.findall(r'\\u[0-9a-fA-F]{4}', cleaned_content))
    }
    
    total_escapes = sum(escape_counts.values())
    if total_escapes > 0:
        logger.info(f"Processing {field_name} with {total_escapes} escape sequences: {escape_counts}")
    
    return cleaned_content


def determine_post_image_type(post_image_radio: str) -> str:
    """Determine the standardized post_image_type value based on radio button selection
    
    This function ensures consistent post_image_type values across all endpoints:
    - "Yes, I have an image URL" → "Yes, Image URL"
    - "Yes, I have an image upload" → "Yes, Upload Image"
    - "Yes, AI generated image" → "Yes, AI Generated"
    - "No image" → "No Image Needed"
    - Empty/None → "No Image Needed"
    - Other values → Keep original value
    
    Args:
        post_image_radio (str): The radio button value from the form
        
    Returns:
        str: Standardized post_image_type value
    """
    logger.info(f"Determining post_image_type for radio value: '{post_image_radio}'")
    
    if not post_image_radio:
        logger.info("No radio value provided, setting to 'No Image Needed'")
        return "No Image Needed"
    
    if "Yes, I have an image URL" in post_image_radio:
        logger.info("Radio contains 'Yes, I have an image URL', setting to 'Yes, Image URL'")
        return "Yes, Image URL"
    elif "Yes, I have an image upload" in post_image_radio:
        logger.info("Radio contains 'Yes, I have an image upload', setting to 'Yes, Upload Image'")
        return "Yes, Upload Image"
    elif "Yes, AI generated image" in post_image_radio:
        logger.info("Radio contains 'Yes, AI generated image', setting to 'Yes, AI Generated'")
        return "Yes, AI Generated"
    elif "No image" in post_image_radio:
        logger.info("Radio contains 'No image', setting to 'No Image Needed'")
        return "No Image Needed"
    else:
        # If radio has a value but doesn't match expected patterns, use the original value
        logger.info(f"Radio value '{post_image_radio}' doesn't match expected patterns, keeping original value")
        return post_image_radio


def handle_image_url_storage(post_data: dict, post_image_type: str) -> dict:
    """Handle image URL storage based on post_image_type selection
    
    This function ensures image URLs are stored in the correct fields:
    - "Yes, Image URL" → store in image_url field, clear uploaded_image_url
    - "Yes, Upload Image" → store in uploaded_image_url field, clear image_url
    - Other types → clear both fields
    
    Args:
        post_data (dict): The post data dictionary
        post_image_type (str): The standardized post_image_type value
        
    Returns:
        dict: Updated post data with proper image URL field assignments
    """
    logger.info(f"Handling image URL storage for post_image_type: '{post_image_type}'")
    
    if post_image_type == "Yes, Image URL":
        # Store external image URL in image_url field, clear uploaded_image_url
        if 'image_url' in post_data:
            post_data['uploaded_image_url'] = None
            logger.info("External image URL stored in image_url field, cleared uploaded_image_url")
        elif 'uploaded_image_url' in post_data:
            # Move uploaded_image_url to image_url and clear uploaded_image_url
            post_data['image_url'] = post_data['uploaded_image_url']
            post_data['uploaded_image_url'] = None
            logger.info("Moved uploaded_image_url to image_url field")
        else:
            logger.info("No image URL provided for external image type")
            
    elif post_image_type == "Yes, Upload Image":
        # Store uploaded image URL in uploaded_image_url field, clear image_url
        if 'uploaded_image_url' in post_data:
            post_data['image_url'] = None
            logger.info("Uploaded image URL stored in uploaded_image_url field, cleared image_url")
        elif 'image_url' in post_data:
            # Move image_url to uploaded_image_url and clear image_url
            post_data['uploaded_image_url'] = post_data['image_url']
            post_data['image_url'] = None
            logger.info("Moved image_url to uploaded_image_url field")
        else:
            logger.info("No image URL provided for upload image type")
            
    else:
        # For AI Generated or No Image Needed, clear both fields
        post_data['image_url'] = None
        post_data['uploaded_image_url'] = None
        logger.info(f"Cleared both image URL fields for post_image_type: '{post_image_type}'")
    
    return post_data

# Wait for database to be ready and create tables
def initialize_database():
    """Initialize database connection and create tables"""
    # Wait for database to be ready
    logger.info("Waiting for SQLite database to be ready...")
    if not wait_for_database(DATABASE_URL, max_retries=10, retry_interval=3):
        logger.error("Failed to connect to database. Exiting...")
        raise RuntimeError("Database connection failed")
    
    # Ensure database exists
    if not ensure_database_exists(DATABASE_URL, max_retries=5, retry_interval=5):
        logger.error("Failed to ensure database exists. Exiting...")
        raise RuntimeError("Database initialization failed")
    
    # Create database tables with retry logic
    max_table_retries = 3
    for attempt in range(max_table_retries):
        try:
            models.Base.metadata.create_all(bind=engine)
            logger.info("SQLite database tables created successfully")
            return
        except Exception as e:
            logger.warning(f"Failed to create database tables (attempt {attempt + 1}/{max_table_retries}): {str(e)}")
            if attempt < max_table_retries - 1:
                import time
                time.sleep(5)
                logger.info("Retrying table creation...")
            else:
                logger.error(f"Failed to create database tables after {max_table_retries} attempts")
                raise RuntimeError(f"Table creation failed: {str(e)}")

# Initialize database with error recovery
try:
    initialize_database()
except RuntimeError as e:
    if "Table creation failed" in str(e):
        logger.warning("Table creation failed, attempting to recreate database...")
        # Wait a bit more for SQLite to be fully ready
        import time
        time.sleep(10)
        try:
            initialize_database()
            logger.info("Database initialization successful on retry")
        except Exception as retry_e:
            logger.error(f"Database initialization failed on retry: {str(retry_e)}")
            raise
    else:
        raise

app = FastAPI(title="n8n Execution Feedback API", version="1.0.0")

# Configure CORS properly
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://104.131.8.230:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"],  # Expose all headers
    max_age=3600,
)

logger.info("CORS middleware configured with origins: %s", [
    "http://localhost:3000",
    "http://104.131.8.230:3000", 
    "http://127.0.0.1:3000"
])

# Additional CORS middleware to ensure headers are always added
@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    """Ensure CORS headers are always added to responses"""
    response = await call_next(request)
    
    # Add CORS headers to all responses
    origin = request.headers.get("origin")
    if origin and origin in [
        "http://localhost:3000",
        "http://104.131.8.230:3000",
        "http://127.0.0.1:3000"
    ]:
        response.headers["Access-Control-Allow-Origin"] = origin
    else:
        response.headers["Access-Control-Allow-Origin"] = "http://104.131.8.230:3000"
    
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Max-Age"] = "3600"
    
    logger.info(f"Added CORS headers for origin: {origin}")
    return response

# Background task to check database health
async def check_database_health():
    """Periodically check database health and recreate if needed"""
    while True:
        try:
            await asyncio.sleep(300)  # Check every 5 minutes
            logger.debug("Performing periodic database health check...")
            
            # Test database connection
            try:
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                logger.debug("Database health check passed")
            except Exception as e:
                logger.warning(f"Database health check failed: {str(e)}")
                logger.info("Attempting to recreate database connection...")
                try:
                    if recreate_engine():
                        logger.info("Database engine recreated successfully")
                    else:
                        logger.warning("Failed to recreate engine, attempting full reinitialization...")
                        initialize_database()
                        logger.info("Database reinitialized successfully")
                except Exception as recreate_e:
                    logger.error(f"Failed to recreate database: {str(recreate_e)}")
                    
        except Exception as e:
            logger.error(f"Error in database health check task: {str(e)}")
            await asyncio.sleep(60)  # Wait 1 minute before retrying

# Start the background task
@app.on_event("startup")
async def startup_event():
    """Start background tasks on startup"""
    # Ensure database is ready on startup
    try:
        logger.info("Performing startup database check...")
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Startup database check passed")
    except Exception as e:
        logger.warning(f"Startup database check failed: {str(e)}")
        logger.info("Attempting to reinitialize database on startup...")
        try:
            initialize_database()
            logger.info("Database reinitialized successfully on startup")
        except Exception as init_e:
            logger.error(f"Failed to reinitialize database on startup: {str(init_e)}")
    
    # Start background health check task
    asyncio.create_task(check_database_health())
    
    # Run Alembic migrations on startup
    try:
        logger.info("Running Alembic migrations on startup...")
        import subprocess
        import sys
        
        # Run alembic upgrade head
        result = subprocess.run([
            sys.executable, "-m", "alembic", "upgrade", "head"
        ], capture_output=True, text=True, cwd="/app")
        
        if result.returncode == 0:
            logger.info("✅ Alembic migrations completed successfully on startup")
            if result.stdout.strip():
                logger.info(f"Migration output: {result.stdout.strip()}")
        else:
            logger.warning(f"⚠️ Alembic migrations failed on startup (exit code: {result.returncode})")
            if result.stderr.strip():
                logger.warning(f"Migration error: {result.stderr.strip()}")
            if result.stdout.strip():
                logger.info(f"Migration output: {result.stdout.strip()}")
    except Exception as e:
        logger.error(f"❌ Failed to run Alembic migrations on startup: {str(e)}")
        logger.info("Server will continue without running migrations")

# Get frontend URL from environment variable or use default
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
logger.info(f"Frontend URL configured as: {FRONTEND_URL}")
logger.info(f"Environment variables: FRONTEND_URL={os.getenv('FRONTEND_URL')}")

# Import the API router
from .api.router import api_router

# Include the API router
app.include_router(api_router)

# Custom middleware to handle JSON parsing errors
@app.middleware("http")
async def json_error_handler(request: Request, call_next):
    """Middleware to catch JSON parsing errors and provide better error messages"""
    try:
        response = await call_next(request)
        return response
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in request: {str(e)}")
        return JSONResponse(
            status_code=400,
            content={
                "detail": [
                    {
                        "type": "json_invalid",
                        "loc": ["body"],
                        "msg": f"Invalid JSON format: {str(e)}",
                        "input": {},
                        "ctx": {
                            "error": str(e),
                            "help": "Please check your JSON syntax, especially quotes and special characters. Make sure all apostrophes and quotes are properly escaped."
                        }
                    }
                ]
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error in middleware: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "detail": [
                    {
                        "type": "internal_error",
                        "loc": ["body"],
                        "msg": "Internal server error",
                        "input": {},
                        "ctx": {"error": str(e)}
                    }
                ]
            }
        )

# All API endpoints have been moved to the new API modules:
# - Feedback endpoints: backend/app/api/feedback.py
# - Social Media endpoints: backend/app/api/social_media.py  
# - Webhook endpoints: backend/app/api/webhooks.py
# - Utility endpoints: backend/app/api/utils.py

logger.info("API endpoints successfully organized into modular structure")
logger.info(f"Using SQLite database: {DATABASE_URL}")