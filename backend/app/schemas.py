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

class FeedbackSubmissionCreateResponse(BaseModel):
    status_code: int
    submission_id: str
    feedback_form_link: str
    message: str

class FeedbackSubmissionUpdate(BaseModel):
    n8n_execution_id: Optional[str] = None
    email: Optional[str] = None
    
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

class FeedbackSubmissionResponse(FeedbackSubmissionBase):
    id: int
    submission_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Social Media Post Schemas
class SocialMediaPostBase(BaseModel):
    content_creator: str
    email: str
    social_platform: str
    custom_content: Optional[str] = None
    ai_prompt: Optional[str] = None
    excluded_llms: Optional[str] = None  # JSON string
    post_image_type: Optional[str] = None
    image_url: Optional[str] = None
    image_file_path: Optional[str] = None
    ai_image_style: Optional[str] = None
    ai_image_description: Optional[str] = None
    status: Optional[str] = "pending"


class SocialMediaPostCreate(SocialMediaPostBase):
    pass


class SocialMediaPostUpdate(BaseModel):
    content_creator: Optional[str] = None
    email: Optional[str] = None
    social_platform: Optional[str] = None
    custom_content: Optional[str] = None
    ai_prompt: Optional[str] = None
    excluded_llms: Optional[str] = None
    post_image_type: Optional[str] = None
    image_url: Optional[str] = None
    image_file_path: Optional[str] = None
    ai_image_style: Optional[str] = None
    ai_image_description: Optional[str] = None
    status: Optional[str] = None


class SocialMediaPostResponse(SocialMediaPostBase):
    id: int
    post_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 