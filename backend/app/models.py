from sqlalchemy import Column, String, Text, DateTime, Integer
from sqlalchemy.sql import func
from .database import Base
import uuid

class FeedbackSubmission(Base):
    __tablename__ = "feedback_submissions"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(String(255), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    
    n8n_execution_id = Column(String(255), nullable=True)
    
    
    email = Column(String(255), nullable=True)
    
    
    linkedin_grok_content = Column(Text)
    linkedin_o3_content = Column(Text)
    linkedin_gemini_content = Column(Text)
    linkedin_feedback = Column(Text)
    linkedin_chosen_llm = Column(String(100))  
    linkedin_custom_content = Column(Text)
    
    
    x_grok_content = Column(Text)
    x_o3_content = Column(Text)
    x_gemini_content = Column(Text)
    x_feedback = Column(Text)
    x_chosen_llm = Column(String(100))  
    x_custom_content = Column(Text)
    
    
    stable_diffusion_image_url = Column(Text)
    pixabay_image_url = Column(Text)
    gpt1_image_url = Column(Text)
    image_feedback = Column(Text)
    image_chosen_llm = Column(String(100))  
    
    
    image_url = Column(Text)  
    uploaded_image_url = Column(Text)  
    
    
    linkedin_image_llm = Column(String(100))  
    twitter_image_llm = Column(String(100))  
    
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SocialMediaPost(Base):
    __tablename__ = "social_media_posts"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(String(255), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    
    content_creator = Column(String(255), nullable=True)  
    email = Column(String(255), nullable=True)
    
    
    feedback_submission_id = Column(String(255), nullable=True)
    
    
    social_platform = Column(String(100), nullable=True)  
    
    
    custom_content = Column(Text)
    ai_prompt = Column(Text)
    
    
    excluded_llms = Column(Text)  
    
    
    post_image_type = Column(String(100))  
    image_url = Column(Text)  
    uploaded_image_url = Column(Text)  
    image_file_path = Column(Text)
    ai_image_style = Column(String(100))
    ai_image_description = Column(Text)
    
    
    linkedin_image_llm = Column(String(100))  
    twitter_image_llm = Column(String(100))  
    
    
    status = Column(String(50), default="pending")  
    
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 