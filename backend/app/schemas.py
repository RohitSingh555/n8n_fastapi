from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

class FeedbackSubmissionBase(BaseModel):
    n8n_execution_id: Optional[str] = None
    email: Optional[str] = None
    
    
    linkedin_grok_content: Optional[str] = None
    linkedin_o3_content: Optional[str] = None
    linkedin_gemini_content: Optional[str] = None
    linkedin_feedback: Optional[str] = None
    linkedin_chosen_llm: Optional[str] = None
    linkedin_custom_content: Optional[str] = None
    
    
    x_grok_content: Optional[str] = None
    x_o3_content: Optional[str] = None
    x_gemini_content: Optional[str] = None
    x_feedback: Optional[str] = None
    x_chosen_llm: Optional[str] = None
    x_custom_content: Optional[str] = None
    
    
    stable_diffusion_image_url: Optional[str] = None
    pixabay_image_url: Optional[str] = None
    gpt1_image_url: Optional[str] = None
    image_feedback: Optional[str] = None
    image_chosen_llm: Optional[str] = None
    
    
    image_url: Optional[str] = None  
    uploaded_image_url: Optional[str] = None  
    
    
    linkedin_image_llm: Optional[str] = None
    twitter_image_llm: Optional[str] = None

    @validator('linkedin_feedback', 'linkedin_chosen_llm', 'linkedin_custom_content', pre=True, always=True)
    def validate_linkedin_feedback_methods(cls, v, values):
        """Ensure only one LinkedIn feedback method is selected"""
        feedback_fields = [
            values.get('linkedin_feedback'),
            values.get('linkedin_chosen_llm'),
            values.get('linkedin_custom_content')
        ]
        filled_fields = [field for field in feedback_fields if field and str(field).strip()]
        if len(filled_fields) > 1:
            raise ValueError('Only one LinkedIn feedback method can be selected at a time')
        return v

    @validator('x_feedback', 'x_chosen_llm', 'x_custom_content', pre=True, always=True)
    def validate_x_feedback_methods(cls, v, values):
        """Ensure only one X/Twitter feedback method is selected"""
        feedback_fields = [
            values.get('x_feedback'),
            values.get('x_chosen_llm'),
            values.get('x_custom_content')
        ]
        filled_fields = [field for field in feedback_fields if field and str(field).strip()]
        if len(filled_fields) > 1:
            raise ValueError('Only one X/Twitter feedback method can be selected at a time')
        return v

    @validator('image_feedback', 'linkedin_image_llm', 'twitter_image_llm', pre=True, always=True)
    def validate_image_feedback_methods(cls, v, values):
        """Ensure only one image feedback method is selected"""
        feedback_fields = [
            values.get('image_feedback'),
            values.get('linkedin_image_llm'),
            values.get('twitter_image_llm')
        ]
        filled_fields = [field for field in feedback_fields if field and str(field).strip()]
        if len(filled_fields) > 1:
            raise ValueError('Only one image feedback method can be selected at a time')
        return v

class FeedbackSubmissionCreate(FeedbackSubmissionBase):
    pass

class FeedbackSubmissionCreateResponse(BaseModel):
    status_code: int
    submission_id: str
    feedback_id: str  
    feedback_form_link: str
    message: str

class FeedbackSubmissionUpdate(BaseModel):
    n8n_execution_id: Optional[str] = None
    email: Optional[str] = None
    
    
    linkedin_grok_content: Optional[str] = None
    linkedin_o3_content: Optional[str] = None
    linkedin_gemini_content: Optional[str] = None
    linkedin_feedback: Optional[str] = None
    linkedin_chosen_llm: Optional[str] = None
    linkedin_custom_content: Optional[str] = None
    
    
    x_grok_content: Optional[str] = None
    x_o3_content: Optional[str] = None
    x_gemini_content: Optional[str] = None
    x_feedback: Optional[str] = None
    x_chosen_llm: Optional[str] = None
    x_custom_content: Optional[str] = None
    
    
    stable_diffusion_image_url: Optional[str] = None
    pixabay_image_url: Optional[str] = None
    gpt1_image_url: Optional[str] = None
    image_feedback: Optional[str] = None
    image_chosen_llm: Optional[str] = None
    
    
    image_url: Optional[str] = None
    uploaded_image_url: Optional[str] = None
    
    
    linkedin_image_llm: Optional[str] = None
    twitter_image_llm: Optional[str] = None

class FeedbackSubmissionResponse(BaseModel):
    
    id: Optional[int] = None
    submission_id: Optional[str] = None
    n8n_execution_id: Optional[str] = None
    email: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    
    linkedin_grok_content: Optional[str] = None
    linkedin_o3_content: Optional[str] = None
    linkedin_gemini_content: Optional[str] = None
    linkedin_feedback: Optional[str] = None
    linkedin_chosen_llm: Optional[str] = None
    linkedin_custom_content: Optional[str] = None
    
    
    x_grok_content: Optional[str] = None
    x_o3_content: Optional[str] = None
    x_gemini_content: Optional[str] = None
    x_feedback: Optional[str] = None
    x_chosen_llm: Optional[str] = None
    x_custom_content: Optional[str] = None
    
    
    stable_diffusion_image_url: Optional[str] = None
    pixabay_image_url: Optional[str] = None
    gpt1_image_url: Optional[str] = None
    image_feedback: Optional[str] = None
    image_chosen_llm: Optional[str] = None
    
    
    image_url: Optional[str] = None
    uploaded_image_url: Optional[str] = None
    
    
    linkedin_image_llm: Optional[str] = None
    twitter_image_llm: Optional[str] = None

    class Config:
        from_attributes = True
        
        extra = "ignore"
        
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }



class SocialMediaPostBase(BaseModel):
    content_creator: Optional[str] = None
    email: Optional[str] = None
    feedback_submission_id: Optional[str] = None
    social_platform: Optional[str] = None
    custom_content: Optional[str] = None
    ai_prompt: Optional[str] = None
    excluded_llms: Optional[str] = None  
    post_image_type: Optional[str] = None
    image_url: Optional[str] = None
    uploaded_image_url: Optional[str] = None
    image_file_path: Optional[str] = None
    ai_image_style: Optional[str] = None
    ai_image_description: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    
    linkedin_image_llm: Optional[str] = None
    twitter_image_llm: Optional[str] = None


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
    uploaded_image_url: Optional[str] = None
    image_file_path: Optional[str] = None
    ai_image_style: Optional[str] = None
    ai_image_description: Optional[str] = None
    status: Optional[str] = None


class SocialMediaPostResponse(BaseModel):
    
    id: Optional[int] = None
    post_id: Optional[str] = None
    content_creator: Optional[str] = None
    email: Optional[str] = None
    feedback_submission_id: Optional[str] = None
    social_platform: Optional[str] = None
    custom_content: Optional[str] = None
    ai_prompt: Optional[str] = None
    excluded_llms: Optional[str] = None
    post_image_type: Optional[str] = None
    image_url: Optional[str] = None
    uploaded_image_url: Optional[str] = None
    image_file_path: Optional[str] = None
    ai_image_style: Optional[str] = None
    ai_image_description: Optional[str] = None
    status: Optional[str] = "pending"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        
        extra = "ignore"
        
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        } 