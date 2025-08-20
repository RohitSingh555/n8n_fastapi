import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import uuid

from app.database import Base
from app.models import FeedbackSubmission


SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)

class TestFeedbackSubmissionModel:
    """Test cases for the FeedbackSubmission model"""
    
    def setup_method(self):
        """Setup method to clear database before each test"""
        self.db = TestingSessionLocal()
        self.db.query(FeedbackSubmission).delete()
        self.db.commit()
    
    def teardown_method(self):
        """Teardown method to close database connection"""
        self.db.close()
    
    def test_create_feedback_submission_with_all_fields(self):
        """Test creating a feedback submission with all fields"""
        feedback = FeedbackSubmission(
            n8n_execution_id="test-execution-123",
            email="test@example.com",
            
            
            linkedin_grok_content="What if AI could transform prenatal care into a lifeline for millions?",
            linkedin_o3_content="What if your next ultrasound could learn from millions of others?",
            linkedin_gemini_content="What if every clinician had a co-pilot in the exam room?",
            linkedin_feedback="Great content, very engaging!",
            linkedin_chosen_llm=None,
            linkedin_custom_content=None,
            
            
            x_grok_content="Sample X Grok content",
            x_o3_content="Sample X o3 content",
            x_gemini_content="Sample X Gemini content",
            x_feedback="X content needs improvement",
            x_chosen_llm=None,
            x_custom_content=None,
            
            
            stable_diffusion_image_url="https://example.com/stable-diffusion.jpg",
            pixabay_image_url="https://example.com/pixabay.jpg",
            gpt1_image_url="https://example.com/gpt1.jpg",
            image_feedback="Images look great!",
            image_chosen_llm=None
        )
        
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        
        
        assert feedback.submission_id is not None
        assert isinstance(feedback.submission_id, str)
        
        
        assert feedback.n8n_execution_id == "test-execution-123"
        assert feedback.email == "test@example.com"
        assert feedback.linkedin_grok_content == "What if AI could transform prenatal care into a lifeline for millions?"
        assert feedback.linkedin_o3_content == "What if your next ultrasound could learn from millions of others?"
        assert feedback.linkedin_gemini_content == "What if every clinician had a co-pilot in the exam room?"
        assert feedback.linkedin_feedback == "Great content, very engaging!"
        assert feedback.linkedin_chosen_llm is None
        assert feedback.linkedin_custom_content is None
        assert feedback.x_grok_content == "Sample X Grok content"
        assert feedback.x_o3_content == "Sample X o3 content"
        assert feedback.x_gemini_content == "Sample X Gemini content"
        assert feedback.x_feedback == "X content needs improvement"
        assert feedback.x_chosen_llm is None
        assert feedback.x_custom_content is None
        assert feedback.stable_diffusion_image_url == "https://example.com/stable-diffusion.jpg"
        assert feedback.pixabay_image_url == "https://example.com/pixabay.jpg"
        assert feedback.gpt1_image_url == "https://example.com/gpt1.jpg"
        assert feedback.image_feedback == "Images look great!"
        assert feedback.image_chosen_llm is None
        
        
        assert feedback.created_at is not None
        assert feedback.updated_at is None  
    
    def test_create_feedback_submission_minimal(self):
        """Test creating a feedback submission with only required fields"""
        feedback = FeedbackSubmission(
            n8n_execution_id="minimal-execution-456",
            email="minimal@example.com"
        )
        
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        
        assert feedback.n8n_execution_id == "minimal-execution-456"
        assert feedback.email == "minimal@example.com"
        assert feedback.submission_id is not None
        
        
        assert feedback.linkedin_feedback is None
        assert feedback.linkedin_chosen_llm is None
        assert feedback.linkedin_custom_content is None
        assert feedback.x_feedback is None
        assert feedback.x_chosen_llm is None
        assert feedback.x_custom_content is None
        assert feedback.image_feedback is None
        assert feedback.image_chosen_llm is None
    
    def test_submission_id_uniqueness(self):
        """Test that submission IDs are unique"""
        feedback1 = FeedbackSubmission(n8n_execution_id="execution-1", email="user1@example.com")
        feedback2 = FeedbackSubmission(n8n_execution_id="execution-2", email="user2@example.com")
        
        self.db.add(feedback1)
        self.db.add(feedback2)
        self.db.commit()
        
        
        self.db.refresh(feedback1)
        self.db.refresh(feedback2)
        
        assert feedback1.submission_id != feedback2.submission_id
        assert feedback1.submission_id is not None
        assert feedback2.submission_id is not None
    
    def test_llm_choices(self):
        """Test that LLM choice fields accept valid values"""
        feedback = FeedbackSubmission(
            n8n_execution_id="llm-test",
            email="llm@example.com",
            linkedin_chosen_llm="Grok",
            x_chosen_llm="o3",
            image_chosen_llm="Pixabay"
        )
        
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        
        assert feedback.linkedin_chosen_llm == "Grok"
        assert feedback.x_chosen_llm == "o3"
        assert feedback.image_chosen_llm == "Pixabay"
    
    def test_mutual_exclusion_validation(self):
        """Test that only one feedback method can be selected at a time"""
        # Test LinkedIn mutual exclusion
        feedback1 = FeedbackSubmission(
            n8n_execution_id="exclusion-test-1",
            email="test1@example.com",
            linkedin_feedback="Feedback text",
            linkedin_chosen_llm="Grok",  # This should cause validation error
            linkedin_custom_content=None
        )
        
        self.db.add(feedback1)
        with pytest.raises(Exception):  # Should raise validation error
            self.db.commit()
        self.db.rollback()
        
        # Test X/Twitter mutual exclusion
        feedback2 = FeedbackSubmission(
            n8n_execution_id="exclusion-test-2",
            email="test2@example.com",
            x_feedback="X feedback text",
            x_chosen_llm="Gemini",  # This should cause validation error
            x_custom_content=None
        )
        
        self.db.add(feedback2)
        with pytest.raises(Exception):  # Should raise validation error
            self.db.commit()
        self.db.rollback()
        
        # Test Image mutual exclusion
        feedback3 = FeedbackSubmission(
            n8n_execution_id="exclusion-test-3",
            email="test3@example.com",
            image_feedback="Image feedback text",
            linkedin_image_llm="Stable",  # This should cause validation error
            twitter_image_llm=None
        )
        
        self.db.add(feedback3)
        with pytest.raises(Exception):  # Should raise validation error
            self.db.commit()
        self.db.rollback()
    
    def test_text_field_lengths(self):
        """Test that text fields can handle long content"""
        long_content = "A" * 10000  
        
        feedback = FeedbackSubmission(
            n8n_execution_id="long-content-test",
            email="long@example.com",
            linkedin_grok_content=long_content,
            linkedin_feedback=long_content,
            linkedin_custom_content=long_content
        )
        
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        
        assert feedback.linkedin_grok_content == long_content
        assert feedback.linkedin_feedback == long_content
        assert feedback.linkedin_custom_content == long_content
    
    def test_url_fields(self):
        """Test that URL fields can handle various URL formats"""
        feedback = FeedbackSubmission(
            n8n_execution_id="url-test",
            email="url@example.com",
            stable_diffusion_image_url="https://example.com/image1.jpg",
            pixabay_image_url="http://pixabay.com/image2.png",
            gpt1_image_url="https://api.openai.com/v1/images/generations"
        )
        
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        
        assert feedback.stable_diffusion_image_url == "https://example.com/image1.jpg"
        assert feedback.pixabay_image_url == "http://pixabay.com/image2.png"
        assert feedback.gpt1_image_url == "https://api.openai.com/v1/images/generations"
    
    def test_required_field_constraint(self):
        """Test that n8n_execution_id and email are required"""
        feedback = FeedbackSubmission()
        
        
        self.db.add(feedback)
        
        
        import pytest
        from sqlalchemy.exc import IntegrityError
        
        with pytest.raises(IntegrityError):
            self.db.commit()
        
        
        self.db.rollback() 