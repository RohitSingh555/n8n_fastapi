from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import List
import uuid
import logging
import traceback
from datetime import datetime
import json
import re

from .. import models, schemas
from ..database import get_db
from ..main import (
    log_escape_characters, 
    validate_and_log_json_content, 
    determine_post_image_type,
    handle_image_url_storage,
    strip_quotes
)

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/feedback", tags=["feedback"])

@router.post("", response_model=schemas.FeedbackSubmissionCreateResponse)
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
            """Clean form values - convert 'string' to None, empty strings to None, and strip quotes"""
            if value is None or value == "" or value == "string":
                return None
            if isinstance(value, str):
                # Strip quotes from string values
                value = strip_quotes(value)
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
        feedback_form_link = f"http://104.131.8.230:3000/feedback/{db_feedback.submission_id}"
        
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

@router.get("", response_model=List[schemas.FeedbackSubmissionResponse])
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

@router.get("/execution/{execution_id}", response_model=List[schemas.FeedbackSubmissionResponse])
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

@router.get("/{submission_id}", response_model=schemas.FeedbackSubmissionResponse)
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
        
        # Also fetch the linked social media post to get image URLs
        social_media_post = db.query(models.SocialMediaPost).filter(
            models.SocialMediaPost.feedback_submission_id == submission_id
        ).first()
        
        # Convert SQLAlchemy model to Pydantic model with explicit field handling
        response_data = {}
        for field in schemas.FeedbackSubmissionResponse.model_fields:
            try:
                value = getattr(feedback, field, None)
                response_data[field] = value if value is not None else None
            except AttributeError:
                # If field doesn't exist on the model, set it to None
                response_data[field] = None
        
        # Populate image URLs from the linked social media post if available
        if social_media_post:
            logger.info(f"Found linked social media post with image_url: {social_media_post.image_url}")
            logger.info(f"Found linked social media post with uploaded_image_url: {social_media_post.uploaded_image_url}")
            response_data['image_url'] = social_media_post.image_url
            response_data['uploaded_image_url'] = social_media_post.uploaded_image_url
        else:
            logger.warning(f"No linked social media post found for feedback submission {submission_id}")
            response_data['image_url'] = None
            response_data['uploaded_image_url'] = None
        
        logger.info(f"Returning response data for submission {submission_id}")
        logger.info(f"Image URLs in response: image_url={response_data.get('image_url')}, uploaded_image_url={response_data.get('uploaded_image_url')}")
        
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

@router.put("/{submission_id}", response_model=schemas.FeedbackSubmissionResponse)
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
        if 'email' in update_data:
            # Strip quotes and whitespace from email
            email_value = strip_quotes(update_data['email']) if isinstance(update_data['email'], str) else update_data['email']
            if not email_value or email_value.strip() == '':
                logger.warning("Email field is empty after cleaning, removing from update data")
                del update_data['email']
            else:
                # Update the email value with the cleaned version
                update_data['email'] = email_value
        
        if update_data:
            # Log escape characters in the update data
            log_escape_characters(update_data, "UPDATE_FEEDBACK")
            
            # Helper function to clean form values
            def clean_form_value(value):
                """Clean form values - convert 'string' to None, empty strings to None, and strip quotes"""
                if value is None or value == "" or value == "string":
                    return None
                if isinstance(value, str):
                    # Strip quotes from string values
                    value = strip_quotes(value)
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
            
            # Also fetch the linked social media post to get image URLs for the response
            social_media_post = db.query(models.SocialMediaPost).filter(
                models.SocialMediaPost.feedback_submission_id == submission_id
            ).first()
            
            # Convert SQLAlchemy model to Pydantic model with explicit field handling
            response_data = {}
            for field in schemas.FeedbackSubmissionResponse.model_fields:
                try:
                    value = getattr(db_feedback, field, None)
                    response_data[field] = value if value is not None else None
                except AttributeError:
                    # If field doesn't exist on the model, set it to None
                    response_data[field] = None
            
            # Populate image URLs from the linked social media post if available
            if social_media_post:
                logger.info(f"Found linked social media post with image_url: {social_media_post.image_url}")
                logger.info(f"Found linked social media post with uploaded_image_url: {social_media_post.uploaded_image_url}")
                response_data['image_url'] = social_media_post.image_url
                response_data['uploaded_image_url'] = social_media_post.uploaded_image_url
            else:
                logger.warning(f"No linked social media post found for feedback submission {submission_id}")
                response_data['image_url'] = None
                response_data['uploaded_image_url'] = None
            
            return schemas.FeedbackSubmissionResponse(**response_data)
        else:
            logger.info(f"No fields to update for submission ID: {submission_id}")
            
            # Also fetch the linked social media post to get image URLs for the response
            social_media_post = db.query(models.SocialMediaPost).filter(
                models.SocialMediaPost.feedback_submission_id == submission_id
            ).first()
            
            # Convert SQLAlchemy model to Pydantic model with explicit field handling
            response_data = {}
            for field in schemas.FeedbackSubmissionResponse.model_fields:
                try:
                    value = getattr(db_feedback, field, None)
                    response_data[field] = value if value is not None else None
                except AttributeError:
                    # If field doesn't exist on the model, set it to None
                    response_data[field] = None
            
            # Populate image URLs from the linked social media post if available
            if social_media_post:
                logger.info(f"Found linked social media post with image_url: {social_media_post.image_url}")
                logger.info(f"Found linked social media post with uploaded_image_url: {social_media_post.uploaded_image_url}")
                response_data['image_url'] = social_media_post.image_url
                response_data['uploaded_image_url'] = social_media_post.uploaded_image_url
            else:
                logger.warning(f"No linked social media post found for feedback submission {submission_id}")
                response_data['image_url'] = None
                response_data['uploaded_image_url'] = None
            
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

@router.put("/raw/{submission_id}")
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
                            # Strip quotes from the value before setting it
                            if isinstance(value, str):
                                value = strip_quotes(value)
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
