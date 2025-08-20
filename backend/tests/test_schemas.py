import pytest
from pydantic import ValidationError
from datetime import datetime

from app.schemas import FeedbackSubmissionCreate, FeedbackSubmissionResponse

class TestFeedbackSubmissionSchemas:
    """Test cases for the Pydantic schemas"""
    
    def test_feedback_submission_create_valid(self):
        """Test creating a valid feedback submission"""
        data = {
            "n8n_execution_id": "test-execution-123",
            "email": "test@example.com",
            "linkedin_grok_content": "What if AI could transform prenatal care into a lifeline for millions?",
            "linkedin_feedback": "Great content!",
            "linkedin_chosen_llm": "Grok",
            "x_feedback": "X content needs improvement",
            "image_feedback": "Images look great!"
        }
        
        feedback = FeedbackSubmissionCreate(**data)
        
        assert feedback.n8n_execution_id == "test-execution-123"
        assert feedback.email == "test@example.com"
        assert feedback.linkedin_grok_content == "What if AI could transform prenatal care into a lifeline for millions?"
        assert feedback.linkedin_feedback == "Great content!"
        assert feedback.linkedin_chosen_llm == "Grok"
        assert feedback.x_feedback == "X content needs improvement"
        assert feedback.image_feedback == "Images look great!"
    
    def test_feedback_submission_create_minimal(self):
        """Test creating a feedback submission with only required fields"""
        data = {
            "n8n_execution_id": "minimal-execution-456",
            "email": "minimal@example.com"
        }
        
        feedback = FeedbackSubmissionCreate(**data)
        
        assert feedback.n8n_execution_id == "minimal-execution-456"
        assert feedback.email == "minimal@example.com"
        assert feedback.linkedin_grok_content is None
        assert feedback.linkedin_feedback is None
        assert feedback.x_feedback is None
        assert feedback.image_feedback is None
    
    def test_feedback_submission_create_missing_required(self):
        """Test that missing required fields raises validation error"""
        data = {
            "linkedin_feedback": "This should fail"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            FeedbackSubmissionCreate(**data)
        
        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert any(error["loc"] == ("n8n_execution_id",) for error in errors)
        assert any(error["loc"] == ("email",) for error in errors)
    
    def test_feedback_submission_create_all_fields(self):
        """Test creating a feedback submission with all possible fields"""
        data = {
            "n8n_execution_id": "complete-execution-789",
            "email": "complete@example.com",
            
            
            "linkedin_grok_content": "What if AI could transform prenatal care into a lifeline for millions?",
            "linkedin_o3_content": "What if your next ultrasound could learn from millions of others?",
            "linkedin_gemini_content": "What if every clinician had a co-pilot in the exam room?",
            "linkedin_feedback": "Great content, very engaging!",
            "linkedin_chosen_llm": "Grok",
            "linkedin_custom_content": "Custom LinkedIn post content",
            
            
            "x_grok_content": "Sample X Grok content",
            "x_o3_content": "Sample X o3 content",
            "x_gemini_content": "Sample X Gemini content",
            "x_feedback": "X content needs improvement",
            "x_chosen_llm": "Gemini",
            "x_custom_content": "Custom X post content",
            
            
            "stable_diffusion_image_url": "https://example.com/stable-diffusion.jpg",
            "pixabay_image_url": "https://example.com/pixabay.jpg",
            "gpt1_image_url": "https://example.com/gpt1.jpg",
            "image_feedback": "Images look great!",
            "image_chosen_llm": "Stable"
        }
        
        feedback = FeedbackSubmissionCreate(**data)
        
        
        assert feedback.n8n_execution_id == "complete-execution-789"
        assert feedback.email == "complete@example.com"
        assert feedback.linkedin_grok_content == "What if AI could transform prenatal care into a lifeline for millions?"
        assert feedback.linkedin_o3_content == "What if your next ultrasound could learn from millions of others?"
        assert feedback.linkedin_gemini_content == "What if every clinician had a co-pilot in the exam room?"
        assert feedback.linkedin_feedback == "Great content, very engaging!"
        assert feedback.linkedin_chosen_llm == "Grok"
        assert feedback.linkedin_custom_content == "Custom LinkedIn post content"
        assert feedback.x_grok_content == "Sample X Grok content"
        assert feedback.x_o3_content == "Sample X o3 content"
        assert feedback.x_gemini_content == "Sample X Gemini content"
        assert feedback.x_feedback == "X content needs improvement"
        assert feedback.x_chosen_llm == "Gemini"
        assert feedback.x_custom_content == "Custom X post content"
        assert feedback.stable_diffusion_image_url == "https://example.com/stable-diffusion.jpg"
        assert feedback.pixabay_image_url == "https://example.com/pixabay.jpg"
        assert feedback.gpt1_image_url == "https://example.com/gpt1.jpg"
        assert feedback.image_feedback == "Images look great!"
        assert feedback.image_chosen_llm == "Stable"
    
    def test_feedback_submission_response_valid(self):
        """Test creating a valid feedback submission response"""
        data = {
            "id": 1,
            "submission_id": "test-submission-123",
            "n8n_execution_id": "test-execution-123",
            "email": "test@example.com",
            "linkedin_grok_content": "What if AI could transform prenatal care into a lifeline for millions?",
            "linkedin_feedback": "Great content!",
            "linkedin_chosen_llm": "Grok",
            "created_at": datetime.now(),
            "updated_at": None
        }
        
        feedback = FeedbackSubmissionResponse(**data)
        
        assert feedback.id == 1
        assert feedback.submission_id == "test-submission-123"
        assert feedback.n8n_execution_id == "test-execution-123"
        assert feedback.email == "test@example.com"
        assert feedback.linkedin_grok_content == "What if AI could transform prenatal care into a lifeline for millions?"
        assert feedback.linkedin_feedback == "Great content!"
        assert feedback.linkedin_chosen_llm == "Grok"
        assert feedback.created_at is not None
        assert feedback.updated_at is None
    
    def test_feedback_submission_response_all_fields(self):
        """Test creating a feedback submission response with all fields"""
        data = {
            "id": 1,
            "submission_id": "complete-submission-456",
            "n8n_execution_id": "complete-execution-456",
            "email": "complete@example.com",
            
            
            "linkedin_grok_content": "What if AI could transform prenatal care into a lifeline for millions?",
            "linkedin_o3_content": "What if your next ultrasound could learn from millions of others?",
            "linkedin_gemini_content": "What if every clinician had a co-pilot in the exam room?",
            "linkedin_feedback": "Great content, very engaging!",
            "linkedin_chosen_llm": "Grok",
            "linkedin_custom_content": "Custom LinkedIn post content",
            
            
            "x_grok_content": "Sample X Grok content",
            "x_o3_content": "Sample X o3 content",
            "x_gemini_content": "Sample X Gemini content",
            "x_feedback": "X content needs improvement",
            "x_chosen_llm": "Gemini",
            "x_custom_content": "Custom X post content",
            
            
            "stable_diffusion_image_url": "https://example.com/stable-diffusion.jpg",
            "pixabay_image_url": "https://example.com/pixabay.jpg",
            "gpt1_image_url": "https://example.com/gpt1.jpg",
            "image_feedback": "Images look great!",
            "image_chosen_llm": "Stable",
            
            
            "created_at": datetime.now(),
            "updated_at": None
        }
        
        feedback = FeedbackSubmissionResponse(**data)
        
        
        assert feedback.id == 1
        assert feedback.submission_id == "complete-submission-456"
        assert feedback.n8n_execution_id == "complete-execution-456"
        assert feedback.email == "complete@example.com"
        assert feedback.linkedin_grok_content == "What if AI could transform prenatal care into a lifeline for millions?"
        assert feedback.linkedin_o3_content == "What if your next ultrasound could learn from millions of others?"
        assert feedback.linkedin_gemini_content == "What if every clinician had a co-pilot in the exam room?"
        assert feedback.linkedin_feedback == "Great content, very engaging!"
        assert feedback.linkedin_chosen_llm == "Grok"
        assert feedback.linkedin_custom_content == "Custom LinkedIn post content"
        assert feedback.x_grok_content == "Sample X Grok content"
        assert feedback.x_o3_content == "Sample X o3 content"
        assert feedback.x_gemini_content == "Sample X Gemini content"
        assert feedback.x_feedback == "X content needs improvement"
        assert feedback.x_chosen_llm == "Gemini"
        assert feedback.x_custom_content == "Custom X post content"
        assert feedback.stable_diffusion_image_url == "https://example.com/stable-diffusion.jpg"
        assert feedback.pixabay_image_url == "https://example.com/pixabay.jpg"
        assert feedback.gpt1_image_url == "https://example.com/gpt1.jpg"
        assert feedback.image_feedback == "Images look great!"
        assert feedback.image_chosen_llm == "Stable"
        assert feedback.created_at is not None
        assert feedback.updated_at is None
    
    def test_llm_choice_validation(self):
        """Test that LLM choice fields accept valid values"""
        valid_llm_choices = ["Grok", "o3", "Gemini", "Stable", "Pixabay", "GPT1"]
        
        for llm in valid_llm_choices:
            data = {
                "n8n_execution_id": f"llm-test-{llm}",
                "email": f"llm-test-{llm}@example.com",
                "linkedin_chosen_llm": llm if llm in ["Grok", "o3", "Gemini"] else None,
                "x_chosen_llm": llm if llm in ["Grok", "o3", "Gemini"] else None,
                "image_chosen_llm": llm if llm in ["Stable", "Pixabay", "GPT1"] else None
            }
            
            feedback = FeedbackSubmissionCreate(**data)
            
            if llm in ["Grok", "o3", "Gemini"]:
                assert feedback.linkedin_chosen_llm == llm or feedback.linkedin_chosen_llm is None
                assert feedback.x_chosen_llm == llm or feedback.x_chosen_llm is None
            if llm in ["Stable", "Pixabay", "GPT1"]:
                assert feedback.image_chosen_llm == llm or feedback.image_chosen_llm is None
    
    def test_mutual_exclusion_validation(self):
        """Test that schemas enforce mutual exclusion between feedback methods"""
        from pydantic import ValidationError
        
        # Test LinkedIn mutual exclusion
        with pytest.raises(ValidationError):
            FeedbackSubmissionCreate(
                n8n_execution_id="exclusion-test",
                email="test@example.com",
                linkedin_feedback="Feedback text",
                linkedin_chosen_llm="Grok",  # This should cause validation error
                linkedin_custom_content=None
            )
        
        # Test X/Twitter mutual exclusion
        with pytest.raises(ValidationError):
            FeedbackSubmissionCreate(
                n8n_execution_id="exclusion-test",
                email="test@example.com",
                x_feedback="X feedback text",
                x_chosen_llm="Gemini",  # This should cause validation error
                x_custom_content=None
            )
        
        # Test Image mutual exclusion
        with pytest.raises(ValidationError):
            FeedbackSubmissionCreate(
                n8n_execution_id="exclusion-test",
                email="test@example.com",
                image_feedback="Image feedback text",
                linkedin_image_llm="Stable",  # This should cause validation error
                twitter_image_llm=None
            )
        
        # Test valid single feedback method selections
        # LinkedIn feedback only
        feedback1 = FeedbackSubmissionCreate(
            n8n_execution_id="valid-test-1",
            email="test@example.com",
            linkedin_feedback="Valid feedback",
            linkedin_chosen_llm=None,
            linkedin_custom_content=None
        )
        assert feedback1.linkedin_feedback == "Valid feedback"
        assert feedback1.linkedin_chosen_llm is None
        assert feedback1.linkedin_custom_content is None
        
        # LinkedIn LLM choice only
        feedback2 = FeedbackSubmissionCreate(
            n8n_execution_id="valid-test-2",
            email="test@example.com",
            linkedin_feedback=None,
            linkedin_chosen_llm="Grok",
            linkedin_custom_content=None
        )
        assert feedback2.linkedin_feedback is None
        assert feedback2.linkedin_chosen_llm == "Grok"
        assert feedback2.linkedin_custom_content is None
    
    def test_url_validation(self):
        """Test that URL fields can handle various URL formats"""
        urls = [
            "https://example.com/image1.jpg",
            "http://pixabay.com/image2.png",
            "https://api.openai.com/v1/images/generations",
            "ftp://example.com/file.txt",
            "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        ]
        
        for url in urls:
            data = {
                "n8n_execution_id": f"url-test-{hash(url)}",
                "email": f"url-test-{hash(url)}@example.com",
                "stable_diffusion_image_url": url,
                "pixabay_image_url": url,
                "gpt1_image_url": url
            }
            
            feedback = FeedbackSubmissionCreate(**data)
            
            assert feedback.stable_diffusion_image_url == url
            assert feedback.pixabay_image_url == url
            assert feedback.gpt1_image_url == url
    
    def test_long_text_validation(self):
        """Test that text fields can handle long content"""
        long_content = "A" * 10000  
        
        data = {
            "n8n_execution_id": "long-text-test",
            "email": "long-text@example.com",
            "linkedin_grok_content": long_content,
            "linkedin_feedback": long_content,
            "linkedin_custom_content": long_content,
            "x_grok_content": long_content,
            "x_feedback": long_content,
            "x_custom_content": long_content,
            "image_feedback": long_content
        }
        
        feedback = FeedbackSubmissionCreate(**data)
        
        assert feedback.linkedin_grok_content == long_content
        assert feedback.linkedin_feedback == long_content
        assert feedback.linkedin_custom_content == long_content
        assert feedback.x_grok_content == long_content
        assert feedback.x_feedback == long_content
        assert feedback.x_custom_content == long_content
        assert feedback.image_feedback == long_content 