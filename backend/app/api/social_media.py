from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import List, Optional
import uuid
import logging
import traceback
from datetime import datetime

from .. import models, schemas
from ..database import get_db
from ..main import (
    determine_post_image_type,
    handle_image_url_storage
)

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/social-media-posts", tags=["social-media"])

@router.post("", response_model=schemas.SocialMediaPostResponse)
def create_social_media_post(
    post: schemas.SocialMediaPostCreate,
    db: Session = Depends(get_db)
):
    """Create a new social media post request"""
    try:
        logger.info(f"Creating social media post for creator: {post.content_creator}")
        
        # Handle post_image_type field with the same logic
        post_data = post.model_dump()
        logger.info(f"Received post data: {post_data}")
        
        if 'post_image_type' in post_data:
            post_data['post_image_type'] = determine_post_image_type(post_data['post_image_type'])
            logger.info(f"Determined post_image_type: {post_data['post_image_type']}")
            
            # Handle image URL storage based on post_image_type
            post_data = handle_image_url_storage(post_data, post_data['post_image_type'])
            logger.info(f"After image URL handling: image_url={post_data.get('image_url')}, uploaded_image_url={post_data.get('uploaded_image_url')}")
        
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

@router.get("", response_model=List[schemas.SocialMediaPostResponse])
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

@router.get("/{post_id}", response_model=schemas.SocialMediaPostResponse)
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

@router.get("/creator/{creator_id}", response_model=List[schemas.SocialMediaPostResponse])
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

@router.put("/{post_id}", response_model=schemas.SocialMediaPostResponse)
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

@router.delete("/{post_id}")
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
