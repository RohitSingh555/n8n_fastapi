from fastapi import APIRouter, Depends, HTTPException, Request, Body
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import uuid
import logging
import traceback
import httpx
import os

from .. import models
from ..database import get_db
from ..main import determine_post_image_type

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api", tags=["webhooks"])

@router.options("/webhook-proxy")
async def webhook_proxy_options():
    """Handle CORS preflight request for webhook-proxy endpoint"""
    return {"message": "OK"}

@router.post("/webhook-proxy")
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
                    """Clean webhook values - convert 'string' to None, empty strings to None, and strip quotes"""
                    if value is None or value == "" or value == "string":
                        return None
                    if isinstance(value, str):
                        # Strip quotes from string values
                        from ..main import strip_quotes
                        value = strip_quotes(value)
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
                
                logger.info(f"Post image radio selection: '{post_image_radio}'")
                logger.info(f"Determined post_image_type: '{post_image_type}'")
                logger.info(f"Webhook data keys: {list(webhook_data.keys())}")
                logger.info(f"Image URL field value: '{webhook_data.get('Image URL', '')}'")
                logger.info(f"Upload an Image field value: '{webhook_data.get('Upload an Image', '')}'")
                
                # Handle image URL storage based on radio button selection
                # Check both "Image URL" and "Upload an Image" fields
                image_url_value = webhook_data.get("Image URL", "")
                upload_image_value = webhook_data.get("Upload an Image", "")
                
                image_url = None
                uploaded_image_url = None
                
                if post_image_type == "Yes, Image URL":
                    # Store external image URL in image_url field
                    image_url = clean_webhook_value(image_url_value) if image_url_value else None
                    uploaded_image_url = None
                    logger.info(f"Storing external image URL: {image_url}")
                elif post_image_type == "Yes, Upload Image":
                    # Store uploaded image URL in uploaded_image_url field
                    image_url = None
                    uploaded_image_url = clean_webhook_value(upload_image_value) if upload_image_value else None
                    logger.info(f"Storing uploaded image URL: {uploaded_image_url}")
                else:
                    # For AI Generated or No Image Needed, clear both fields
                    image_url = None
                    uploaded_image_url = None
                    logger.info(f"No image needed, cleared both URL fields")
                
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
                logger.info(f"Social media post image_url: {social_media_post.image_url}")
                logger.info(f"Social media post uploaded_image_url: {social_media_post.uploaded_image_url}")
                logger.info(f"Feedback form link: {feedback_form_link}")
                
                # Add the feedback URL and ID to the webhook data
                webhook_data["Feedback Form URL"] = feedback_form_link
                webhook_data["Feedback Submission ID"] = feedback_submission.submission_id
                webhook_data["Social Media Post ID"] = social_media_post.post_id
                
                # Add the new image LLM fields to the webhook data
                webhook_data["LinkedIn Image LLM"] = social_media_post.linkedin_image_llm
                webhook_data["Twitter Image LLM"] = social_media_post.twitter_image_llm
                
                # Add the image URLs to the webhook data
                webhook_data["Image URL"] = social_media_post.image_url
                webhook_data["Upload an Image"] = social_media_post.uploaded_image_url
                
                logger.info(f"Added to webhook data - Image URL: {webhook_data['Image URL']}")
                logger.info(f"Added to webhook data - Upload an Image: {webhook_data['Upload an Image']}")
                
                # Clean all webhook data values before sending
                for key in webhook_data:
                    webhook_data[key] = clean_webhook_value(webhook_data[key])
                
                # Helper function to preserve all fields but clean values
                def clean_webhook_data(data_dict):
                    """Clean webhook values but preserve all fields - convert 'string' to None, empty strings to empty strings, and strip quotes"""
                    cleaned = {}
                    for key, value in data_dict.items():
                        if value == "string":
                            cleaned[key] = None
                        elif isinstance(value, str):
                            # Strip quotes from string values
                            from ..main import strip_quotes
                            cleaned[key] = strip_quotes(value)
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

@router.post("/submit-feedback-webhook")
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
        
        # Log whether we found the social media post and its data
        if social_media_post:
            logger.info(f"Found social media post with ID: {social_media_post.post_id}")
            logger.info(f"Social media post image_url: {social_media_post.image_url}")
            logger.info(f"Social media post uploaded_image_url: {social_media_post.uploaded_image_url}")
        else:
            logger.warning(f"No social media post found for feedback submission ID: {feedback_submission.submission_id}")
            logger.warning("This means the image URLs will be null in the webhook")
        
        # Helper function to clean webhook values
        def clean_webhook_value(value):
            """Clean webhook values - convert 'string' placeholder to None, but preserve actual null values, and strip quotes"""
            if value == "string":  # Only convert placeholder 'string' to None
                return None
            if isinstance(value, str):
                # Strip quotes from string values
                from ..main import strip_quotes
                value = strip_quotes(value)
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
            
            # Additional Image Fields from Social Media Post (these are the actual image URLs)
            "feedback_image_url": clean_webhook_value(social_media_post.image_url if social_media_post else None),
            "feedback_uploaded_image_url": clean_webhook_value(social_media_post.uploaded_image_url if social_media_post else None),
            
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
        
        # Log the image URL values being sent to the webhook for debugging
        logger.info(f"Webhook payload image_url: {webhook_payload.get('image_url')}")
        logger.info(f"Webhook payload uploaded_image_url: {webhook_payload.get('uploaded_image_url')}")
        logger.info(f"Webhook payload feedback_image_url: {webhook_payload.get('feedback_image_url')}")
        logger.info(f"Webhook payload feedback_uploaded_image_url: {webhook_payload.get('feedback_uploaded_image_url')}")
        logger.info(f"Social media post image_url: {social_media_post.image_url if social_media_post else None}")
        logger.info(f"Social media post uploaded_image_url: {social_media_post.uploaded_image_url if social_media_post else None}")
        logger.info(f"Feedback submission image_url: {feedback_submission.image_url}")
        logger.info(f"Feedback submission uploaded_image_url: {feedback_submission.uploaded_image_url}")
        
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
