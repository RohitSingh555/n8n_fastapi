from sqlalchemy import Column, String, Text, DateTime, Integer
from sqlalchemy.sql import func
from .database import Base
import uuid

class FeedbackSubmission(Base):
    __tablename__ = "feedback_submissions"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # n8n Execution ID
    n8n_execution_id = Column(String, nullable=False)
    
    # User Email
    email = Column(String, nullable=False)
    
    # LinkedIn Content
    linkedin_grok_content = Column(Text)
    linkedin_o3_content = Column(Text)
    linkedin_gemini_content = Column(Text)
    linkedin_feedback = Column(Text)
    linkedin_chosen_llm = Column(String)  # Grok, o3, Gemini
    linkedin_custom_content = Column(Text)
    
    # X Content
    x_grok_content = Column(Text)
    x_o3_content = Column(Text)
    x_gemini_content = Column(Text)
    x_feedback = Column(Text)
    x_chosen_llm = Column(String)  # Grok, o3, Gemini
    x_custom_content = Column(Text)
    
    # Image URLs
    stable_diffusion_image_url = Column(Text)
    pixabay_image_url = Column(Text)
    gpt1_image_url = Column(Text)
    image_feedback = Column(Text)
    image_chosen_llm = Column(String)  # Stable, Pixabay, GPT1
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 