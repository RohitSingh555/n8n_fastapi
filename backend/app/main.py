from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import uuid

from . import models, schemas
from .database import engine, get_db

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
    db_feedback = models.FeedbackSubmission(
        submission_id=str(uuid.uuid4()),
        **feedback.dict()
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

@app.get("/api/feedback/{submission_id}", response_model=schemas.FeedbackSubmissionResponse)
def get_feedback_by_submission_id(submission_id: str, db: Session = Depends(get_db)):
    """Get feedback submission by submission ID"""
    feedback = db.query(models.FeedbackSubmission).filter(
        models.FeedbackSubmission.submission_id == submission_id
    ).first()
    if feedback is None:
        raise HTTPException(status_code=404, detail="Feedback submission not found")
    return feedback

@app.get("/api/feedback", response_model=List[schemas.FeedbackSubmissionResponse])
def get_all_feedback_submissions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all feedback submissions with pagination"""
    feedback_submissions = db.query(models.FeedbackSubmission).offset(skip).limit(limit).all()
    return feedback_submissions

@app.get("/api/feedback/execution/{execution_id}", response_model=List[schemas.FeedbackSubmissionResponse])
def get_feedback_by_execution_id(execution_id: str, db: Session = Depends(get_db)):
    """Get feedback submissions by n8n execution ID"""
    feedback_submissions = db.query(models.FeedbackSubmission).filter(
        models.FeedbackSubmission.n8n_execution_id == execution_id
    ).all()
    return feedback_submissions

@app.get("/")
def read_root():
    return {"message": "n8n Execution Feedback API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"} 