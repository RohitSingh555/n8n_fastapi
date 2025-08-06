from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FeedbackSubmissionBase(BaseModel):
    n8n_execution_id: str
    email: str
    
    # LinkedIn Content
    linkedin_grok_content: Optional[str] = None
    linkedin_o3_content: Optional[str] = None
    linkedin_gemini_content: Optional[str] = None
    linkedin_feedback: Optional[str] = None
    linkedin_chosen_llm: Optional[str] = None
    linkedin_custom_content: Optional[str] = None
    
    # X Content
    x_grok_content: Optional[str] = None
    x_o3_content: Optional[str] = None
    x_gemini_content: Optional[str] = None
    x_feedback: Optional[str] = None
    x_chosen_llm: Optional[str] = None
    x_custom_content: Optional[str] = None
    
    # Image URLs
    stable_diffusion_image_url: Optional[str] = None
    pixabay_image_url: Optional[str] = None
    gpt1_image_url: Optional[str] = None
    image_feedback: Optional[str] = None
    image_chosen_llm: Optional[str] = None

class FeedbackSubmissionCreate(FeedbackSubmissionBase):
    pass

class FeedbackSubmissionResponse(FeedbackSubmissionBase):
    id: int
    submission_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 