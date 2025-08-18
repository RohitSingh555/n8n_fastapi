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
    - "Image URL" → "Yes, Image URL"
    - "Upload Image" → "Yes, Upload Image"
    - "AI Generated" → "Yes, AI Generated"
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
    
    if "Image URL" in post_image_radio:
        logger.info("Radio contains 'Image URL', setting to 'Yes, Image URL'")
        return "Yes, Image URL"
    elif "Upload Image" in post_image_radio:
        logger.info("Radio contains 'Upload Image', setting to 'Yes, Upload Image'")
        return "Yes, Upload Image"
    elif "AI Generated" in post_image_radio:
        logger.info("Radio contains 'AI Generated', setting to 'Yes, AI Generated'")
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
    logger.info("Waiting for MySQL database to be ready...")
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
            logger.info("Database tables created successfully")
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
        # Wait a bit more for MySQL to be fully ready
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

# Test endpoint to verify CORS is working
@app.get("/api/test-cors")
async def test_cors():
    """Test endpoint to verify CORS is working correctly"""
    logger.info("CORS test endpoint called")
    return {"message": "CORS is working", "timestamp": datetime.utcnow().isoformat()}











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

# Add OPTIONS handlers for CORS preflight
@app.options("/api/feedback")
async def options_feedback():
    return {"message": "OK"}

@app.options("/api/feedback/{submission_id}")
async def options_feedback_by_id(submission_id: str):
    """Handle CORS preflight request for feedback by ID endpoint"""
    logger.info(f"OPTIONS request for /api/feedback/{submission_id}")
    return {"message": "OK"}

@app.options("/api/submit-feedback-webhook")
async def options_webhook():
    return {"message": "OK"}

@app.options("/api/feedback-raw/{submission_id}")
async def options_feedback_raw(submission_id: str):
    return {"message": "OK"}

@app.post("/api/feedback", response_model=schemas.FeedbackSubmissionCreateResponse)
def create_feedback_submission(
    feedback: schemas.FeedbackSubmissionCreate,
    db: Session = Depends(get_db)
):
    """Create a new feedback submission"""
    try:
        logger.info(f"Creating feedback submission for execution_id: {feedback.n8n_execution_id}")
        
        # Log escape characters in the incoming data
        feedback_data = feedback.model_dump()
        log_escape_characters(feedback_data, "CREATE_FEEDBACK")
        
        # Helper function to clean form values
        def clean_form_value(value):
            """Clean form values - convert 'string' to None, empty strings to None"""
            if value is None or value == "" or value == "string":
                return None
            return value
        
        # Clean all form values before saving to database
        for field_name, field_value in feedback_data.items():
            if isinstance(field_value, str):
                feedback_data[field_name] = clean_form_value(field_value)
            elif field_value is not None:
                feedback_data[field_name] = validate_and_log_json_content(field_value, field_name)
        
        db_feedback = models.FeedbackSubmission(
            submission_id=str(uuid.uuid4()),
            **feedback_data
        )
        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)
        
        logger.info(f"Successfully created feedback submission with ID: {db_feedback.submission_id}")
        
        # Create the response with the required format
        feedback_form_link = f"{FRONTEND_URL}/feedback/{db_feedback.submission_id}"
        
        return schemas.FeedbackSubmissionCreateResponse(
            status_code=201,
            submission_id=db_feedback.submission_id,
            feedback_id=db_feedback.submission_id,  # Added feedback_id for webhook
            feedback_form_link=feedback_form_link,
            message="Feedback submission was stored successfully! You can provide feedback using the link above."
        )
        
    except IntegrityError as e:
        logger.error(f"Database integrity error: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=400, 
            detail=f"Database integrity error: {str(e)}"
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error creating feedback submission: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/api/feedback", response_model=List[schemas.FeedbackSubmissionResponse])
def get_all_feedback_submissions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all feedback submissions with pagination"""
    try:
        logger.info(f"Fetching all feedback submissions with skip={skip}, limit={limit}")
        
        feedback_submissions = db.query(models.FeedbackSubmission).offset(skip).limit(limit).all()
        
        logger.info(f"Successfully retrieved {len(feedback_submissions)} feedback submissions")
        # Convert SQLAlchemy models to Pydantic models with explicit field handling
        response_list = []
        for feedback in feedback_submissions:
            response_data = {}
            for field in schemas.FeedbackSubmissionResponse.model_fields:
                value = getattr(feedback, field, None)
                response_data[field] = value if value is not None else None
            response_list.append(schemas.FeedbackSubmissionResponse(**response_data))
        return response_list
        
    except SQLAlchemyError as e:
        logger.error(f"Database error fetching all feedback submissions: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error fetching all feedback submissions: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/api/feedback/execution/{execution_id}", response_model=List[schemas.FeedbackSubmissionResponse])
def get_feedback_by_execution_id(execution_id: str, db: Session = Depends(get_db)):
    """Get feedback submissions by n8n execution ID"""
    try:
        logger.info(f"Fetching feedback submissions for execution_id: {execution_id}")
        
        feedback_submissions = db.query(models.FeedbackSubmission).filter(
            models.FeedbackSubmission.n8n_execution_id == execution_id
        ).all()
        
        logger.info(f"Successfully retrieved {len(feedback_submissions)} feedback submissions for execution_id: {execution_id}")
        # Convert SQLAlchemy models to Pydantic models with explicit field handling
        response_list = []
        for feedback in feedback_submissions:
            response_data = {}
            for field in schemas.FeedbackSubmissionResponse.model_fields:
                value = getattr(feedback, field, None)
                response_data[field] = value if value is not None else None
            response_list.append(schemas.FeedbackSubmissionResponse(**response_data))
        return response_list
        
    except SQLAlchemyError as e:
        logger.error(f"Database error fetching feedback by execution_id: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error fetching feedback by execution_id: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/api/feedback/{submission_id}", response_model=schemas.FeedbackSubmissionResponse)
def get_feedback_by_submission_id(submission_id: str, request: Request, db: Session = Depends(get_db)):
    """Get feedback submission by submission ID"""
    logger.info(f"GET /api/feedback/{submission_id} endpoint called")
    logger.info(f"Request received for submission ID: {submission_id}")
    logger.info(f"Request headers: {dict(request.headers)}")
    logger.info(f"Request method: {request.method}")
    logger.info(f"Request URL: {request.url}")
    try:
        logger.info(f"Fetching feedback submission with ID: {submission_id}")
        
        feedback = db.query(models.FeedbackSubmission).filter(
            models.FeedbackSubmission.submission_id == submission_id
        ).first()
        
        if feedback is None:
            logger.warning(f"Feedback submission not found with ID: {submission_id}")
            raise HTTPException(status_code=404, detail="Feedback submission not found")
        
        logger.info(f"Successfully retrieved feedback submission with ID: {submission_id}")
        # Convert SQLAlchemy model to Pydantic model with explicit field handling
        response_data = {}
        for field in schemas.FeedbackSubmissionResponse.model_fields:
            try:
                value = getattr(feedback, field, None)
                response_data[field] = value if value is not None else None
            except AttributeError:
                # If field doesn't exist on the model, set it to None
                response_data[field] = None
        
        logger.info(f"Returning response data for submission {submission_id}")
        
        # Return the Pydantic model directly - FastAPI will handle serialization
        return schemas.FeedbackSubmissionResponse(**response_data)
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error fetching feedback submission: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error fetching feedback submission: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )

@app.put("/api/feedback/{submission_id}", response_model=schemas.FeedbackSubmissionResponse)
def update_feedback_submission(
    submission_id: str,
    feedback_update: schemas.FeedbackSubmissionUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing feedback submission"""
    try:
        logger.info(f"Updating feedback submission with ID: {submission_id}")
        logger.info(f"Update data received: {feedback_update.model_dump()}")
        
        # Get existing feedback submission
        db_feedback = db.query(models.FeedbackSubmission).filter(
            models.FeedbackSubmission.submission_id == submission_id
        ).first()
        
        if db_feedback is None:
            logger.warning(f"Feedback submission not found with ID: {submission_id}")
            raise HTTPException(status_code=404, detail="Feedback submission not found")
        
        logger.info(f"Found existing feedback: {db_feedback.submission_id}")
        
        # Update only the fields that are provided
        update_data = feedback_update.model_dump(exclude_unset=True)
        logger.info(f"Fields to update: {list(update_data.keys())}")
        
        # Filter out any database-specific fields that shouldn't be updated
        forbidden_fields = {'id', 'submission_id', 'created_at'}
        update_data = {k: v for k, v in update_data.items() if k not in forbidden_fields}
        logger.info(f"Filtered fields to update: {list(update_data.keys())}")
        
        # Ensure email is not empty if it's being updated
        if 'email' in update_data and (not update_data['email'] or update_data['email'].strip() == ''):
            logger.warning("Email field is empty, removing from update data")
            del update_data['email']
        
        if update_data:
            # Log escape characters in the update data
            log_escape_characters(update_data, "UPDATE_FEEDBACK")
            
            # Helper function to clean form values
            def clean_form_value(value):
                """Clean form values - convert 'string' to None, empty strings to None"""
                if value is None or value == "" or value == "string":
                    return None
                return value
            
            # Clean all form values before updating database
            for field_name, field_value in update_data.items():
                if isinstance(field_value, str):
                    update_data[field_name] = clean_form_value(field_value)
                elif field_value is not None:
                    update_data[field_name] = validate_and_log_json_content(field_value, field_name)
            
            update_data['updated_at'] = datetime.utcnow()
            
            for field, value in update_data.items():
                logger.info(f"Setting field {field} to {value}")
                setattr(db_feedback, field, value)
            
            db.commit()
            db.refresh(db_feedback)
            
            logger.info(f"Successfully updated feedback submission with ID: {submission_id}")
            # Convert SQLAlchemy model to Pydantic model with explicit field handling
            response_data = {}
            for field in schemas.FeedbackSubmissionResponse.model_fields:
                try:
                    value = getattr(db_feedback, field, None)
                    response_data[field] = value if value is not None else None
                except AttributeError:
                    # If field doesn't exist on the model, set it to None
                    response_data[field] = None
            return schemas.FeedbackSubmissionResponse(**response_data)
        else:
            logger.info(f"No fields to update for submission ID: {submission_id}")
            # Convert SQLAlchemy model to Pydantic model with explicit field handling
            response_data = {}
            for field in schemas.FeedbackSubmissionResponse.model_fields:
                try:
                    value = getattr(db_feedback, field, None)
                    response_data[field] = value if value is not None else None
                except AttributeError:
                    # If field doesn't exist on the model, set it to None
                    response_data[field] = None
            return schemas.FeedbackSubmissionResponse(**response_data)
            
    except HTTPException:
        raise
    except IntegrityError as e:
        logger.error(f"Database integrity error updating feedback submission: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=400, 
            detail=f"Database integrity error: {str(e)}"
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error updating feedback submission: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
            logger.error(f"Unexpected error updating feedback submission: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            db.rollback()
            
            # Return more detailed error information
            error_detail = f"Internal server error: {str(e)}"
            if "datetime" in str(e).lower():
                error_detail = "Date/time format error. Please check the data being sent."
            elif "validation" in str(e).lower():
                error_detail = "Data validation error. Please check the field values."
            
            raise HTTPException(
                status_code=500, 
                detail=error_detail
            )

# Alternative PUT endpoint that handles raw JSON for better error handling
@app.put("/api/feedback-raw/{submission_id}")
async def update_feedback_submission_raw(
    submission_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Update an existing feedback submission with raw JSON handling"""
    try:
        logger.info(f"Updating feedback submission with ID: {submission_id} using raw JSON")
        
        # Get existing feedback submission
        db_feedback = db.query(models.FeedbackSubmission).filter(
            models.FeedbackSubmission.submission_id == submission_id
        ).first()
        
        if db_feedback is None:
            logger.warning(f"Feedback submission not found with ID: {submission_id}")
            raise HTTPException(status_code=404, detail="Feedback submission not found")
        
        # Parse raw JSON body
        try:
            body = await request.body()
            raw_data = json.loads(body.decode('utf-8'))
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            # Try to clean the JSON string manually
            try:
                body_str = body.decode('utf-8')
                logger.info(f"Attempting to clean JSON string. Original length: {len(body_str)}")
                
                # More aggressive cleaning approach
                cleaned_str = body_str
                
                # Replace problematic apostrophes with escaped ones
                if "'" in cleaned_str:
                    cleaned_str = cleaned_str.replace("'", "\\'")
                    logger.info("Replaced unescaped apostrophes")
                
                # Handle newlines and other control characters in string values
                # Simple approach: replace all newlines and control characters globally
                cleaned_str = cleaned_str.replace('\n', '\\n')
                cleaned_str = cleaned_str.replace('\r', '\\r')
                cleaned_str = cleaned_str.replace('\t', '\\t')
                
                # Remove other control characters
                cleaned_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', cleaned_str)
                
                logger.info("Cleaned control characters from JSON string")
                
                # Try to parse the cleaned JSON
                raw_data = json.loads(cleaned_str)
                logger.info("Successfully cleaned and parsed JSON after initial failure")
                
            except Exception as clean_error:
                logger.error(f"Failed to clean JSON: {str(clean_error)}")
                # Provide more detailed error information
                body_str = body.decode('utf-8')
                error_pos = e.pos
                context_start = max(0, error_pos - 100)
                context_end = min(len(body_str), error_pos + 100)
                context = body_str[context_start:context_end]
                
                raise HTTPException(
                    status_code=400,
                    detail={
                        "type": "json_invalid",
                        "msg": f"Invalid JSON format: {str(e)}",
                        "error_position": error_pos,
                        "context": context,
                        "help": "Please check your JSON syntax, especially quotes and special characters. Make sure all apostrophes and quotes are properly escaped. The error occurred around the highlighted context."
                    }
                )
        
        # Update only the fields that are provided
        if raw_data:
            # Log escape characters in the update data
            log_escape_characters(raw_data, "UPDATE_FEEDBACK_RAW")
            
            # Validate and log content with escape characters
            for field_name, field_value in raw_data.items():
                if isinstance(field_value, str) and field_value:
                    raw_data[field_name] = validate_and_log_json_content(field_value, field_name)
            
            raw_data['updated_at'] = datetime.utcnow()
            
            for field, value in raw_data.items():
                if hasattr(db_feedback, field):
                    # Special handling for n8n_execution_id: only update if current value is empty/None
                    if field == 'n8n_execution_id':
                        current_value = getattr(db_feedback, field)
                        if current_value is None or current_value == '':
                            logger.info(f"Updating n8n_execution_id from '{current_value}' to '{value}'")
                            setattr(db_feedback, field, value)
                        else:
                            logger.info(f"Skipping n8n_execution_id update - current value '{current_value}' is not empty")
                    else:
                        # For all other fields, update normally
                        logger.info(f"Updating field '{field}' to '{value}'")
                        setattr(db_feedback, field, value)
        
        db.commit()
        db.refresh(db_feedback)
        
        logger.info(f"Successfully updated feedback submission with ID: {submission_id}")
        # Return the updated feedback submission object to match the response_model
        return db_feedback
            
    except HTTPException:
        raise
    except IntegrityError as e:
        logger.error(f"Database integrity error updating feedback submission: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=400, 
            detail=f"Database integrity error: {str(e)}"
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error updating feedback submission: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error updating feedback submission: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/")
def read_root():
    """Root endpoint"""
    try:
        logger.info("Root endpoint accessed")
        return {"message": "n8n Execution Feedback API", "version": "1.0.0"}
    except Exception as e:
        logger.error(f"Error in root endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
def health_check():
    """Health check endpoint"""
    try:
        # Only log health checks at DEBUG level to reduce noise
        logger.debug("Health check endpoint accessed")
        
        # Test database connection
        try:
            db = next(get_db())
            db.execute(text("SELECT 1"))
            db.close()
            db_status = "connected"
        except Exception as db_error:
            logger.error(f"Database connection error: {str(db_error)}")
            db_status = f"error: {str(db_error)}"
        
        return {
            "status": "healthy", 
            "message": "API is running",
            "database": db_status,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in health check endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Health check failed")

@app.get("/migrations/status")
def migration_status():
    """Check Alembic migration status"""
    try:
        logger.info("Migration status endpoint accessed")
        
        import subprocess
        import sys
        
        # Get current migration status
        result = subprocess.run([
            sys.executable, "-m", "alembic", "current"
        ], capture_output=True, text=True, cwd="/app")
        
        current_migration = "unknown"
        if result.returncode == 0 and result.stdout.strip():
            current_migration = result.stdout.strip()
        
        # Get migration history
        history_result = subprocess.run([
            sys.executable, "-m", "alembic", "history", "--verbose"
        ], capture_output=True, text=True, cwd="/app")
        
        migration_history = []
        if history_result.returncode == 0 and history_result.stdout.strip():
            migration_history = history_result.stdout.strip().split('\n')
        
        return {
            "status": "success",
            "current_migration": current_migration,
            "migration_history": migration_history[:10],  # Last 10 migrations
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in migration status endpoint: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@app.get("/migrations/run")
def run_migrations():
    """Manually trigger Alembic migrations"""
    try:
        logger.info("Manual migration trigger endpoint accessed")
        
        import subprocess
        import sys
        
        # Run alembic upgrade head
        result = subprocess.run([
            sys.executable, "-m", "alembic", "upgrade", "head"
        ], capture_output=True, text=True, cwd="/app")
        
        if result.returncode == 0:
            logger.info("✅ Manual migrations completed successfully")
            return {
                "status": "success",
                "message": "Migrations completed successfully",
                "output": result.stdout.strip(),
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            logger.warning(f"⚠️ Manual migrations failed (exit code: {result.returncode})")
            return {
                "status": "error",
                "message": "Migrations failed",
                "error": result.stderr.strip(),
                "output": result.stdout.strip(),
                "exit_code": result.returncode,
                "timestamp": datetime.utcnow().isoformat()
            }
    except Exception as e:
        logger.error(f"Error in manual migration endpoint: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@app.post("/api/test-escape-characters")
def test_escape_characters_endpoint(data: dict):
    """Test endpoint to verify escape character handling"""
    try:
        logger.info("Testing escape character handling endpoint")
        
        # Log all escape characters found in the request
        log_escape_characters(data, "TEST_ESCAPE_CHARACTERS")
        
        # Process and validate each field
        processed_data = {}
        for field_name, field_value in data.items():
            if isinstance(field_value, str) and field_value:
                processed_data[field_name] = validate_and_log_json_content(field_value, field_name)
            else:
                processed_data[field_name] = field_value
        
        # Return both original and processed data for comparison
        return {
            "message": "Escape character test completed",
            "original_data": data,
            "processed_data": processed_data,
            "escape_character_summary": {
                "total_fields": len(data),
                "string_fields": len([v for v in data.values() if isinstance(v, str)]),
                "fields_with_escapes": len([v for v in processed_data.values() if isinstance(v, str) and any(esc in v for esc in ['\\n', '\\t', '\\r', '\\b', '\\f', '\\"', '\\\\'])]
            )
        }}
        
    except Exception as e:
        logger.error(f"Error in escape character test endpoint: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Test endpoint error: {str(e)}")

@app.post("/api/test-json-parsing")
async def test_json_parsing_endpoint(request: Request):
    """Test endpoint to debug JSON parsing issues"""
    try:
        logger.info("Testing JSON parsing endpoint")
        
        # Get raw body
        body = await request.body()
        body_str = body.decode('utf-8')
        
        # Try to parse JSON
        try:
            parsed_data = json.loads(body_str)
            return {
                "message": "JSON parsed successfully",
                "body_length": len(body_str),
                "parsed_data": parsed_data,
                "status": "success"
            }
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            
            # Try to identify the problematic character
            error_pos = e.pos
            context_start = max(0, error_pos - 50)
            context_end = min(len(body_str), error_pos + 50)
            context = body_str[context_start:context_end]
            
            # Try to clean common issues
            cleaned_str = body_str
            if "'" in body_str:
                cleaned_str = body_str.replace("'", "\\'")
                logger.info("Attempted to clean apostrophes")
            
            try:
                cleaned_data = json.loads(cleaned_str)
                return {
                    "message": "JSON parsed after cleaning",
                    "original_error": str(e),
                    "error_position": error_pos,
                    "context": context,
                    "cleaned_data": cleaned_data,
                    "status": "cleaned"
                }
            except:
                return {
                    "message": "JSON parsing failed even after cleaning",
                    "error": str(e),
                    "error_position": error_pos,
                    "context": context,
                    "body_preview": body_str[:200] + "..." if len(body_str) > 200 else body_str,
                    "status": "failed"
                }
        
    except Exception as e:
        logger.error(f"Error in JSON parsing test endpoint: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Test endpoint error: {str(e)}")

@app.post("/api/fix-json")
async def fix_json_endpoint(request: Request):
    """Endpoint to automatically fix common JSON issues"""
    try:
        logger.info("Fixing JSON endpoint accessed")
        
        # Get raw body
        body = await request.body()
        body_str = body.decode('utf-8')
        
        # Try to parse JSON first
        try:
            parsed_data = json.loads(body_str)
            return {
                "message": "JSON was already valid",
                "fixed_json": body_str,
                "status": "already_valid"
            }
        except json.JSONDecodeError as e:
            logger.info(f"Attempting to fix JSON: {str(e)}")
            
            # Fix common issues
            fixed_str = body_str
            
            # Replace unescaped apostrophes in string values
            # This regex finds apostrophes that are inside quotes but not escaped
            import re
            
            # Pattern to match string values and fix apostrophes
            def fix_apostrophes(match):
                content = match.group(1)
                # Replace unescaped apostrophes with escaped ones
                fixed_content = content.replace("'", "\\'")
                return f'"{fixed_content}"'
            
            # Find all string values and fix them
            string_pattern = r'"([^"]*)"'
            fixed_str = re.sub(string_pattern, fix_apostrophes, fixed_str)
            
            # Try to parse the fixed JSON
            try:
                fixed_data = json.loads(fixed_str)
                return {
                    "message": "JSON fixed successfully",
                    "original_json": body_str,
                    "fixed_json": fixed_str,
                    "parsed_data": fixed_data,
                    "status": "fixed"
                }
            except json.JSONDecodeError as fix_error:
                return {
                    "message": "Failed to fix JSON",
                    "original_error": str(e),
                    "fix_error": str(fix_error),
                    "original_json": body_str,
                    "attempted_fix": fixed_str,
                    "status": "failed"
                }
        
    except Exception as e:
        logger.error(f"Error in fix JSON endpoint: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Fix JSON endpoint error: {str(e)}")

@app.post("/api/debug-json")
async def debug_json_endpoint(request: Request):
    """Debug endpoint to show exactly what's wrong with JSON"""
    try:
        logger.info("Debug JSON endpoint accessed")
        
        # Get raw body
        body = await request.body()
        body_str = body.decode('utf-8')
        
        # Show the raw body and identify issues
        issues = []
        
        # Check for newlines
        newline_count = body_str.count('\n')
        if newline_count > 0:
            issues.append(f"Found {newline_count} newline characters")
        
        # Check for unescaped apostrophes
        apostrophe_count = body_str.count("'")
        if apostrophe_count > 0:
            issues.append(f"Found {apostrophe_count} apostrophe characters")
        
        # Check for control characters
        control_chars = []
        for i, char in enumerate(body_str):
            if ord(char) < 32 and char not in '\n\r\t':
                control_chars.append(f"Position {i}: {repr(char)} (char code {ord(char)})")
        
        if control_chars:
            issues.append(f"Found control characters: {control_chars}")
        
        # Try to show where the problem is
        try:
            json.loads(body_str)
            return {
                "message": "JSON is valid",
                "body_length": len(body_str),
                "issues": issues,
                "status": "valid"
            }
        except json.JSONDecodeError as e:
            # Show the problematic area
            error_pos = e.pos
            context_start = max(0, error_pos - 100)
            context_end = min(len(body_str), error_pos + 100)
            context = body_str[context_start:context_end]
            
            # Show the character at the error position
            problem_char = body_str[error_pos] if error_pos < len(body_str) else "EOF"
            
            return {
                "message": "JSON is invalid",
                "error": str(e),
                "error_position": error_pos,
                "problem_character": repr(problem_char),
                "context": context,
                "body_length": len(body_str),
                "issues": issues,
                "status": "invalid"
            }
        
    except Exception as e:
        logger.error(f"Error in debug JSON endpoint: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Debug JSON endpoint error: {str(e)}")


@app.post("/api/test-post-image-type")
def test_post_image_type_endpoint(data: dict):
    """Test endpoint to verify post_image_type logic"""
    try:
        logger.info("Testing post_image_type logic endpoint")
        
        # Test the determine_post_image_type function with various inputs
        test_cases = [
            ("Image URL", "Yes, Image URL"),
            ("Upload Image", "Yes, Upload Image"),
            ("AI Generated", "Yes, AI Generated"),
            ("", "No Image Needed"),
            (None, "No Image Needed"),
            ("Some other value", "Some other value"),
            ("Image URL with extra text", "Yes, Image URL"),
            ("Upload Image and more", "Yes, Upload Image"),
            ("AI Generated content", "Yes, AI Generated")
        ]
        
        results = []
        for input_val, expected in test_cases:
            actual = determine_post_image_type(input_val)
            results.append({
                "input": input_val,
                "expected": expected,
                "actual": actual,
                "matches": expected
            })
        
        # Test with the provided data if it contains post_image_type
        if 'post_image_type' in data:
            provided_result = determine_post_image_type(data['post_image_type'])
            results.append({
                "input": data['post_image_type'],
                "expected": "custom input",
                "actual": provided_result,
                "matches": True
            })
        
        # Test the handle_image_url_storage function
        image_url_tests = [
            ("Yes, Image URL", {"image_url": "https://example.com/image.jpg", "uploaded_image_url": "https://upload.com/img.jpg"}),
            ("Yes, Upload Image", {"image_url": "https://example.com/image.jpg", "uploaded_image_url": "https://upload.com/img.jpg"}),
            ("Yes, AI Generated", {"image_url": "https://example.com/image.jpg", "uploaded_image_url": "https://upload.com/img.jpg"}),
            ("No Image Needed", {"image_url": "https://example.com/image.jpg", "uploaded_image_url": "https://upload.com/img.jpg"})
        ]
        
        image_url_results = []
        for post_image_type, test_data in image_url_tests:
            result = handle_image_url_storage(test_data.copy(), post_image_type)
            image_url_results.append({
                "post_image_type": post_image_type,
                "input": test_data,
                "output": result
            })
        
        return {
            "message": "Post image type logic and image URL storage test completed",
            "post_image_type_tests": results,
            "image_url_storage_tests": image_url_results,
            "all_tests_passed": all(r["matches"] for r in results),
            "functions_working": True
        }
        
    except Exception as e:
        logger.error(f"Error in post image type test endpoint: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Test endpoint error: {str(e)}")


# Social Media Post Endpoints
@app.post("/api/social-media-posts", response_model=schemas.SocialMediaPostResponse)
def create_social_media_post(
    post: schemas.SocialMediaPostCreate,
    db: Session = Depends(get_db)
):
    """Create a new social media post request"""
    try:
        logger.info(f"Creating social media post for creator: {post.content_creator}")
        
        # Handle post_image_type field with the same logic
        post_data = post.model_dump()
        if 'post_image_type' in post_data:
            post_data['post_image_type'] = determine_post_image_type(post_data['post_image_type'])
            
            # Handle image URL storage based on post_image_type
            post_data = handle_image_url_storage(post_data, post_data['post_image_type'])
        
        db_post = models.SocialMediaPost(
            post_id=str(uuid.uuid4()),
            **post_data
        )
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        
        logger.info(f"Successfully created social media post with ID: {db_post.post_id}")
        return db_post
        
    except IntegrityError as e:
        logger.error(f"Database integrity error: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=400, 
            detail=f"Database integrity error: {str(e)}"
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error creating social media post: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/api/social-media-posts", response_model=List[schemas.SocialMediaPostResponse])
def get_all_social_media_posts(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all social media posts with optional filtering by status"""
    try:
        logger.info(f"Fetching social media posts with skip={skip}, limit={limit}, status={status}")
        
        query = db.query(models.SocialMediaPost)
        
        if status:
            query = query.filter(models.SocialMediaPost.status == status)
        
        posts = query.offset(skip).limit(limit).all()
        
        logger.info(f"Successfully retrieved {len(posts)} social media posts")
        return posts
        
    except SQLAlchemyError as e:
        logger.error(f"Database error fetching social media posts: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error fetching social media posts: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/api/social-media-posts/{post_id}", response_model=schemas.SocialMediaPostResponse)
def get_social_media_post_by_id(post_id: str, db: Session = Depends(get_db)):
    """Get social media post by post ID"""
    try:
        logger.info(f"Fetching social media post with ID: {post_id}")
        
        post = db.query(models.SocialMediaPost).filter(
            models.SocialMediaPost.post_id == post_id
        ).first()
        
        if post is None:
            logger.warning(f"Social media post not found with ID: {post_id}")
            raise HTTPException(status_code=404, detail="Social media post not found")
        
        logger.info(f"Successfully retrieved social media post with ID: {post_id}")
        return post
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error fetching social media post: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error fetching social media post: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/api/social-media-posts/creator/{creator_id}", response_model=List[schemas.SocialMediaPostResponse])
def get_social_media_posts_by_creator(creator_id: str, db: Session = Depends(get_db)):
    """Get social media posts by content creator ID"""
    try:
        logger.info(f"Fetching social media posts for creator: {creator_id}")
        
        posts = db.query(models.SocialMediaPost).filter(
            models.SocialMediaPost.content_creator == creator_id
        ).all()
        
        logger.info(f"Successfully retrieved {len(posts)} social media posts for creator: {creator_id}")
        return posts
        
    except SQLAlchemyError as e:
        logger.error(f"Database error fetching posts by creator: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error fetching posts by creator: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )


@app.put("/api/social-media-posts/{post_id}", response_model=schemas.SocialMediaPostResponse)
def update_social_media_post(
    post_id: str,
    post_update: schemas.SocialMediaPostUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing social media post"""
    try:
        logger.info(f"Updating social media post with ID: {post_id}")
        
        # Get existing post
        db_post = db.query(models.SocialMediaPost).filter(
            models.SocialMediaPost.post_id == post_id
        ).first()
        
        if db_post is None:
            logger.warning(f"Social media post not found with ID: {post_id}")
            raise HTTPException(status_code=404, detail="Social media post not found")
        
        # Update only the fields that are provided
        update_data = post_update.model_dump(exclude_unset=True)
        if update_data:
            # Handle post_image_type field with the same logic as creation
            if 'post_image_type' in update_data:
                update_data['post_image_type'] = determine_post_image_type(update_data['post_image_type'])
                
                # Handle image URL storage based on post_image_type
                update_data = handle_image_url_storage(update_data, update_data['post_image_type'])
            
            update_data['updated_at'] = datetime.utcnow()
            
            for field, value in update_data.items():
                setattr(db_post, field, value)
            
            db.commit()
            db.refresh(db_post)
            
            logger.info(f"Successfully updated social media post with ID: {post_id}")
            return db_post
        else:
            logger.info(f"No fields to update for post ID: {post_id}")
            return db_post
            
    except HTTPException:
        raise
    except IntegrityError as e:
        logger.error(f"Database integrity error updating social media post: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=400, 
            detail=f"Database integrity error: {str(e)}"
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error updating social media post: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error updating social media post: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )


@app.delete("/api/social-media-posts/{post_id}")
def delete_social_media_post(post_id: str, db: Session = Depends(get_db)):
    """Delete a social media post"""
    try:
        logger.info(f"Deleting social media post with ID: {post_id}")
        
        db_post = db.query(models.SocialMediaPost).filter(
            models.SocialMediaPost.post_id == post_id
        ).first()
        
        if db_post is None:
            logger.warning(f"Social media post not found with ID: {post_id}")
            raise HTTPException(status_code=404, detail="Social media post not found")
        
        db.delete(db_post)
        db.commit()
        
        logger.info(f"Successfully deleted social media post with ID: {post_id}")
        return {"message": "Social media post deleted successfully"}
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error deleting social media post: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error deleting social media post: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )


@app.post("/api/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """Upload image to external server and return the URL"""
    try:
        logger.info(f"Uploading image: {file.filename}")
        
        # Read the file content
        file_content = await file.read()
        
        # Prepare form data for the external server
        files = {"files": (file.filename, file_content, file.content_type)}
        
        # Upload to external server
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://165.227.123.243:8000/upload",
                files=files,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Successfully uploaded image: {file.filename}")
                return result
            else:
                logger.error(f"External server error: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"External server error: {response.text}"
                )
                
    except httpx.TimeoutException:
        logger.error("Timeout uploading image to external server")
        raise HTTPException(status_code=408, detail="Upload timeout")
    except httpx.RequestError as e:
        logger.error(f"Request error uploading image: {str(e)}")
        raise HTTPException(status_code=502, detail=f"External server error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error uploading image: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.options("/api/webhook-proxy")
async def webhook_proxy_options():
    """Handle CORS preflight request for webhook-proxy endpoint"""
    return {"message": "OK"}

@app.post("/api/webhook-proxy")
async def proxy_webhook(request: Request, data: list = Body(...), db: Session = Depends(get_db)):
    """Proxy webhook requests to n8n webhook to avoid CORS issues and create feedback entry
    
    This endpoint handles CORS preflight requests and forwards webhook data to n8n.
    """
    logger.info(f"Webhook proxy endpoint called with data length: {len(data) if data else 0}")
    logger.info(f"Request headers: {dict(request.headers)}")
    
    try:
        logger.info("Proxying webhook request to n8n and creating feedback entry")
        
        # Extract data from the first item in the list (assuming single submission)
        if data and len(data) > 0:
            webhook_data = data[0]
            
            # Create an empty feedback entry in the database
            try:
                # Generate a unique execution ID for this social media post
                execution_id = f"sm-{str(uuid.uuid4())}"
                
                # Extract email from the webhook data
                email = webhook_data.get("Content Creator", "")
                
                # Helper function to clean webhook values
                def clean_webhook_value(value):
                    """Clean webhook values - convert 'string' to None, empty strings to None"""
                    if value is None or value == "" or value == "string":
                        return None
                    return value
                
                # Create empty feedback submission
                feedback_submission = models.FeedbackSubmission(
                    submission_id=str(uuid.uuid4()),
                    n8n_execution_id=execution_id,
                    email=email,
                    # All other fields will be NULL (empty) as requested
                )
                
                db.add(feedback_submission)
                
                # Also create a social media post entry
                # Determine post_image_type based on radio button selection
                post_image_radio = webhook_data.get("Post Image?", "")
                post_image_type = determine_post_image_type(post_image_radio)
                
                # Handle image URL storage based on radio button selection
                original_image_url = webhook_data.get("Image URL", "")
                image_url = None
                uploaded_image_url = None
                
                if post_image_type == "Yes, Image URL":
                    # Store external image URL in image_url field
                    image_url = original_image_url
                    uploaded_image_url = None
                elif post_image_type == "Yes, Upload Image":
                    # Store uploaded image URL in uploaded_image_url field
                    image_url = None
                    uploaded_image_url = original_image_url
                else:
                    # For AI Generated or No Image Needed, clear both fields
                    image_url = None
                    uploaded_image_url = None
                
                social_media_post = models.SocialMediaPost(
                    post_id=str(uuid.uuid4()),
                    content_creator=clean_webhook_value(webhook_data.get("Content Creator", "")),
                    email=email,
                    feedback_submission_id=feedback_submission.submission_id,  # Link to feedback submission
                    social_platform=clean_webhook_value(webhook_data.get("Social Platforms", "")),
                    custom_content=clean_webhook_value(webhook_data.get("Custom Content?", "")),
                    ai_prompt=clean_webhook_value(webhook_data.get("AI Prompted Text Generation", "")),
                    excluded_llms=clean_webhook_value(webhook_data.get("Exclude LLMs", "")),
                    post_image_type=post_image_type,
                    image_url=image_url,
                    uploaded_image_url=uploaded_image_url,
                    linkedin_image_llm=clean_webhook_value(webhook_data.get("LinkedIn Image LLM", "")),
                    twitter_image_llm=clean_webhook_value(webhook_data.get("Twitter Image LLM", "")),
                    status="pending"
                )
                
                db.add(social_media_post)
                db.commit()
                db.refresh(feedback_submission)
                db.refresh(social_media_post)
                
                # Create the feedback form link
                feedback_form_link = f"http://104.131.8.230:3000/feedback/{feedback_submission.submission_id}"
                
                logger.info(f"Created empty feedback entry with ID: {feedback_submission.submission_id}")
                logger.info(f"Created social media post entry with ID: {social_media_post.post_id}")
                logger.info(f"Feedback form link: {feedback_form_link}")
                
                # Add the feedback URL and ID to the webhook data
                webhook_data["Feedback Form URL"] = feedback_form_link
                webhook_data["Feedback Submission ID"] = feedback_submission.submission_id
                webhook_data["Social Media Post ID"] = social_media_post.post_id
                
                # Add the new image LLM fields to the webhook data
                webhook_data["LinkedIn Image LLM"] = social_media_post.linkedin_image_llm
                webhook_data["Twitter Image LLM"] = social_media_post.twitter_image_llm
                
                # Clean all webhook data values before sending
                for key in webhook_data:
                    webhook_data[key] = clean_webhook_value(webhook_data[key])
                
                # Helper function to preserve all fields but clean values
                def clean_webhook_data(data_dict):
                    """Clean webhook values but preserve all fields - convert 'string' to None, empty strings to empty strings"""
                    cleaned = {}
                    for key, value in data_dict.items():
                        if value == "string":
                            cleaned[key] = None
                        else:
                            cleaned[key] = value
                    return cleaned
                
                # Clean all webhook data values but preserve all fields
                webhook_data = clean_webhook_data(webhook_data)
                
                # Update the data list with the modified webhook data
                data[0] = webhook_data
                
            except Exception as e:
                logger.error(f"Failed to create database entries: {str(e)}")
                # Continue with webhook forwarding even if database creation fails
                db.rollback()
        
        # Forward the request to the n8n webhook
        async with httpx.AsyncClient() as client:
            # Get webhook URL from environment variable
            webhook_url = os.getenv("N8N_WEBHOOK_URL", "https://ultrasoundai.app.n8n.cloud/webhook/1ef36a73-0e04-4cf5-ae0c-c3f1dca496ba")
            
            response = await client.post(
                webhook_url,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=30.0
            )
            
            if response.status_code == 200:
                logger.info("Successfully forwarded webhook request to n8n")
                return {
                    "message": "Webhook request forwarded successfully",
                    "feedback_form_link": feedback_form_link if 'feedback_form_link' in locals() else None,
                    "feedback_submission_id": feedback_submission.submission_id if 'feedback_submission' in locals() else None,
                    "social_media_post_id": social_media_post.post_id if 'social_media_post' in locals() else None
                }
            else:
                logger.error(f"N8n webhook error: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"N8n webhook error: {response.text}"
                )
                
    except httpx.TimeoutException:
        logger.error("Timeout forwarding webhook request to n8n")
        raise HTTPException(status_code=408, detail="Webhook timeout")
    except httpx.RequestError as e:
        logger.error(f"Request error forwarding webhook: {str(e)}")
        raise HTTPException(status_code=502, detail=f"Webhook error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error forwarding webhook: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/api/submit-feedback-webhook")
async def submit_feedback_webhook(
    feedback_data: dict = Body(...),
    db: Session = Depends(get_db)
):
    """Submit feedback data to the specified webhook URL with both social media and feedback data"""
    try:
        logger.info("Submitting feedback data to webhook")
        
        # Extract submission ID and get the complete data from database
        submission_id = feedback_data.get("submission_id")
        if not submission_id:
            raise HTTPException(status_code=400, detail="submission_id is required")
        
        # Get feedback submission data
        feedback_submission = db.query(models.FeedbackSubmission).filter(
            models.FeedbackSubmission.submission_id == submission_id
        ).first()
        
        if not feedback_submission:
            raise HTTPException(status_code=404, detail="Feedback submission not found")
        
        # Get social media post data linked to this feedback submission
        social_media_post = db.query(models.SocialMediaPost).filter(
            models.SocialMediaPost.feedback_submission_id == feedback_submission.submission_id
        ).first()
        
        # Helper function to clean webhook values
        def clean_webhook_value(value):
            """Clean webhook values - convert 'string' placeholder to None, but preserve actual null values"""
            if value == "string":  # Only convert placeholder 'string' to None
                return None
            return value  # Return the value as-is (including None, empty strings, etc.)
        
        # Prepare the webhook payload with all data - always include every field
        webhook_payload = {
            # Social Media Form Data
            "content_creator": clean_webhook_value(social_media_post.content_creator if social_media_post else None),
            "email": feedback_submission.email,
            "social_platforms": clean_webhook_value(social_media_post.social_platform if social_media_post else None),
            "custom_content": clean_webhook_value(social_media_post.custom_content if social_media_post else None),
            "ai_prompt": clean_webhook_value(social_media_post.ai_prompt if social_media_post else None),
            "excluded_llms": clean_webhook_value(social_media_post.excluded_llms if social_media_post else None),
            "post_image_type": clean_webhook_value(social_media_post.post_image_type if social_media_post else None),
            "image_url": clean_webhook_value(social_media_post.image_url if social_media_post else None),
            "uploaded_image_url": clean_webhook_value(social_media_post.uploaded_image_url if social_media_post else None),
            "ai_image_style": clean_webhook_value(social_media_post.ai_image_style if social_media_post else None),
            "ai_image_description": clean_webhook_value(social_media_post.ai_image_description if social_media_post else None),
            "status": clean_webhook_value(social_media_post.status if social_media_post else None),
            
            # Feedback Data
            "n8n_execution_id": feedback_submission.n8n_execution_id,
            "submission_id": feedback_submission.submission_id,
            
            # LinkedIn Content
            "linkedin_grok_content": clean_webhook_value(feedback_submission.linkedin_grok_content),
            "linkedin_o3_content": clean_webhook_value(feedback_submission.linkedin_o3_content),
            "linkedin_gemini_content": clean_webhook_value(feedback_submission.linkedin_gemini_content),
            "linkedin_feedback": clean_webhook_value(feedback_submission.linkedin_feedback),
            "linkedin_chosen_llm": clean_webhook_value(feedback_submission.linkedin_chosen_llm),
            "linkedin_custom_content": clean_webhook_value(feedback_submission.linkedin_custom_content),
            
            # X Content
            "x_grok_content": clean_webhook_value(feedback_submission.x_grok_content),
            "x_o3_content": clean_webhook_value(feedback_submission.x_o3_content),
            "x_gemini_content": clean_webhook_value(feedback_submission.x_gemini_content),
            "x_feedback": clean_webhook_value(feedback_submission.x_feedback),
            "x_chosen_llm": clean_webhook_value(feedback_submission.x_chosen_llm),
            "x_custom_content": clean_webhook_value(feedback_submission.x_custom_content),
            
            # Image URLs
            "stable_diffusion_image_url": clean_webhook_value(feedback_submission.stable_diffusion_image_url),
            "pixabay_image_url": clean_webhook_value(feedback_submission.pixabay_image_url),
            "gpt1_image_url": clean_webhook_value(feedback_submission.gpt1_image_url),
            "image_feedback": clean_webhook_value(feedback_submission.image_feedback),
            "image_chosen_llm": clean_webhook_value(feedback_submission.image_chosen_llm),
            
            # Additional Image Fields from Feedback Submission
            "feedback_image_url": clean_webhook_value(feedback_submission.image_url),
            "feedback_uploaded_image_url": clean_webhook_value(feedback_submission.uploaded_image_url),
            
            # Separate Image LLM selections for platforms
            "linkedin_image_llm": clean_webhook_value(feedback_submission.linkedin_image_llm),
            "twitter_image_llm": clean_webhook_value(feedback_submission.twitter_image_llm),
            
            # Timestamps
            "created_at": feedback_submission.created_at.isoformat() if feedback_submission.created_at else None,
            "updated_at": feedback_submission.updated_at.isoformat() if feedback_submission.updated_at else None
        }
        
        # Always send all fields - no filtering of null/empty values
        
        # Always include the new image LLM fields even if they're empty
        # This ensures they appear in n8n for users to fill out
        webhook_payload["LinkedIn Image LLM"] = feedback_submission.linkedin_image_llm or ""
        webhook_payload["Twitter Image LLM"] = feedback_submission.twitter_image_llm or ""
        
        # Submit to the specified webhook URL
        webhook_url = "https://ultrasoundai.app.n8n.cloud/webhook/3f455a01-2e10-4605-9a9c-d2e6da548bb5"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                webhook_url,
                json=webhook_payload,
                headers={"Content-Type": "application/json"},
                timeout=30.0
            )
            
            if response.status_code == 200:
                logger.info("Successfully submitted feedback data to webhook")
                return {
                    "message": "Feedback data submitted to webhook successfully",
                    "webhook_response": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
                    "status_code": response.status_code
                }
            else:
                logger.error(f"Webhook error: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Webhook error: {response.text}"
                )
                
    except httpx.TimeoutException:
        logger.error("Timeout submitting feedback data to webhook")
        raise HTTPException(status_code=408, detail="Webhook timeout")
    except httpx.RequestError as e:
        logger.error(f"Request error submitting feedback data: {str(e)}")
        raise HTTPException(status_code=502, detail=f"Webhook error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error submitting feedback data: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")