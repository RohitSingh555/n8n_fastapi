from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import List, Optional
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


# Social Media Post Endpoints
@app.post("/api/social-media-posts", response_model=schemas.SocialMediaPostResponse)
def create_social_media_post(
    post: schemas.SocialMediaPostCreate,
    db: Session = Depends(get_db)
):
    """Create a new social media post request"""
    try:
        logger.info(f"Creating social media post for creator: {post.content_creator}")
        
        db_post = models.SocialMediaPost(
            post_id=str(uuid.uuid4()),
            **post.model_dump()
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