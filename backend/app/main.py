from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import List
import uuid
import logging
import traceback
from datetime import datetime

from . import models, schemas
from .database import engine, get_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="n8n Execution Feedback API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/feedback", response_model=schemas.FeedbackSubmissionResponse)
def create_feedback_submission(
    feedback: schemas.FeedbackSubmissionCreate,
    db: Session = Depends(get_db)
):
    """Create a new feedback submission"""
    try:
        logger.info(f"Creating feedback submission for execution_id: {feedback.n8n_execution_id}")
        
        db_feedback = models.FeedbackSubmission(
            submission_id=str(uuid.uuid4()),
            **feedback.model_dump()
        )
        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)
        
        logger.info(f"Successfully created feedback submission with ID: {db_feedback.submission_id}")
        return db_feedback
        
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
        return feedback_submissions
        
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
        return feedback_submissions
        
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
def get_feedback_by_submission_id(submission_id: str, db: Session = Depends(get_db)):
    """Get feedback submission by submission ID"""
    try:
        logger.info(f"Fetching feedback submission with ID: {submission_id}")
        
        feedback = db.query(models.FeedbackSubmission).filter(
            models.FeedbackSubmission.submission_id == submission_id
        ).first()
        
        if feedback is None:
            logger.warning(f"Feedback submission not found with ID: {submission_id}")
            raise HTTPException(status_code=404, detail="Feedback submission not found")
        
        logger.info(f"Successfully retrieved feedback submission with ID: {submission_id}")
        return feedback
        
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
        
        # Get existing feedback submission
        db_feedback = db.query(models.FeedbackSubmission).filter(
            models.FeedbackSubmission.submission_id == submission_id
        ).first()
        
        if db_feedback is None:
            logger.warning(f"Feedback submission not found with ID: {submission_id}")
            raise HTTPException(status_code=404, detail="Feedback submission not found")
        
        # Update only the fields that are provided
        update_data = feedback_update.model_dump(exclude_unset=True)
        if update_data:
            update_data['updated_at'] = datetime.utcnow()
            
            for field, value in update_data.items():
                setattr(db_feedback, field, value)
            
            db.commit()
            db.refresh(db_feedback)
            
            logger.info(f"Successfully updated feedback submission with ID: {submission_id}")
            return db_feedback
        else:
            logger.info(f"No fields to update for submission ID: {submission_id}")
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
        logger.info("Health check endpoint accessed")
        return {"status": "healthy", "message": "API is running"}
    except Exception as e:
        logger.error(f"Error in health check endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Health check failed") 