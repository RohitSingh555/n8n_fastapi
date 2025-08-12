from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Body
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

from . import models, schemas
from .database import engine, get_db, DATABASE_URL
from .database_utils import wait_for_database, ensure_database_exists

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Wait for database to be ready and create tables
def initialize_database():
    """Initialize database connection and create tables"""
    # Wait for database to be ready
    logger.info("Waiting for MySQL database to be ready...")
    if not wait_for_database(DATABASE_URL, max_retries=10, retry_interval=3):
        logger.error("Failed to connect to database. Exiting...")
        raise RuntimeError("Database connection failed")
    
    # Ensure database exists
    if not ensure_database_exists(DATABASE_URL):
        logger.error("Failed to ensure database exists. Exiting...")
        raise RuntimeError("Database initialization failed")
    
    # Create database tables
    try:
        models.Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")
        raise RuntimeError(f"Table creation failed: {str(e)}")

# Initialize database
initialize_database()

app = FastAPI(title="n8n Execution Feedback API", version="1.0.0")

# Get frontend URL from environment variable or use default
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React app URL
        "http://104.131.8.230:3000",  # Production frontend URL
        FRONTEND_URL,  # Environment variable frontend URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/feedback", response_model=schemas.FeedbackSubmissionCreateResponse)
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


@app.post("/api/webhook-proxy")
async def proxy_webhook(data: list = Body(...), db: Session = Depends(get_db)):
    """Proxy webhook requests to n8n webhook to avoid CORS issues and create feedback entry"""
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
                
                # Create empty feedback submission
                feedback_submission = models.FeedbackSubmission(
                    submission_id=str(uuid.uuid4()),
                    n8n_execution_id=execution_id,
                    email=email,
                    # All other fields will be NULL (empty) as requested
                )
                
                db.add(feedback_submission)
                
                # Also create a social media post entry
                social_media_post = models.SocialMediaPost(
                    post_id=str(uuid.uuid4()),
                    content_creator=webhook_data.get("Content Creator", ""),
                    email=email,
                    social_platform=webhook_data.get("Social Platforms", ""),
                    custom_content=webhook_data.get("Custom Content?", ""),
                    ai_prompt=webhook_data.get("AI Prompted Text Generation", ""),
                    excluded_llms=webhook_data.get("Exclude LLMs", ""),
                    post_image_type=webhook_data.get("Post Image?", ""),
                    image_url=webhook_data.get("Image URL", ""),
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
                
                # Update the data list with the modified webhook data
                data[0] = webhook_data
                
            except Exception as e:
                logger.error(f"Failed to create database entries: {str(e)}")
                # Continue with webhook forwarding even if database creation fails
                db.rollback()
        
        # Forward the request to the n8n webhook
        async with httpx.AsyncClient() as client:
            # Get webhook URL from environment variable
            webhook_url = os.getenv("N8N_WEBHOOK_URL", "https://ultrasoundai.app.n8n.cloud/webhook/b2d454f5-3dde-4d56-9bff-5e1f23b7d94b")
            
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
        
        # Get social media post data
        social_media_post = db.query(models.SocialMediaPost).filter(
            models.SocialMediaPost.email == feedback_submission.email
        ).first()
        
        # Prepare the webhook payload with all data
        webhook_payload = {
            # Social Media Form Data
            "content_creator": social_media_post.content_creator if social_media_post else "",
            "email": feedback_submission.email,
            "social_platforms": social_media_post.social_platform if social_media_post else "",
            "custom_content": social_media_post.custom_content if social_media_post else "",
            "ai_prompt": social_media_post.ai_prompt if social_media_post else "",
            "excluded_llms": social_media_post.excluded_llms if social_media_post else "",
            "post_image_type": social_media_post.post_image_type if social_media_post else "",
            "image_url": social_media_post.image_url if social_media_post else "",
            "ai_image_style": social_media_post.ai_image_style if social_media_post else "",
            "ai_image_description": social_media_post.ai_image_description if social_media_post else "",
            "status": social_media_post.status if social_media_post else "",
            
            # Feedback Data
            "n8n_execution_id": feedback_submission.n8n_execution_id,
            "submission_id": feedback_submission.submission_id,
            
            # LinkedIn Content
            "linkedin_grok_content": feedback_submission.linkedin_grok_content,
            "linkedin_o3_content": feedback_submission.linkedin_o3_content,
            "linkedin_gemini_content": feedback_submission.linkedin_gemini_content,
            "linkedin_feedback": feedback_submission.linkedin_feedback,
            "linkedin_chosen_llm": feedback_submission.linkedin_chosen_llm,
            "linkedin_custom_content": feedback_submission.linkedin_custom_content,
            
            # X Content
            "x_grok_content": feedback_submission.x_grok_content,
            "x_o3_content": feedback_submission.x_o3_content,
            "x_gemini_content": feedback_submission.x_gemini_content,
            "x_feedback": feedback_submission.x_feedback,
            "x_chosen_llm": feedback_submission.x_chosen_llm,
            "x_custom_content": feedback_submission.x_custom_content,
            
            # Image URLs
            "stable_diffusion_image_url": feedback_submission.stable_diffusion_image_url,
            "pixabay_image_url": feedback_submission.pixabay_image_url,
            "gpt1_image_url": feedback_submission.gpt1_image_url,
            "image_feedback": feedback_submission.image_feedback,
            "image_chosen_llm": feedback_submission.image_chosen_llm,
            
            # Timestamps
            "created_at": feedback_submission.created_at.isoformat() if feedback_submission.created_at else None,
            "updated_at": feedback_submission.updated_at.isoformat() if feedback_submission.updated_at else None
        }
        
        # Submit to the specified webhook URL
        webhook_url = "https://ultrasoundai.app.n8n.cloud/webhook-test/3f455a01-2e10-4605-9a9c-d2e6da548bb5"
        
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