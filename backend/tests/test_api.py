import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db, Base
from app.models import FeedbackSubmission

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

class TestFeedbackAPI:
    """Test cases for the feedback API endpoints"""
    
    def setup_method(self):
        """Setup method to clear database before each test"""
        db = TestingSessionLocal()
        db.query(FeedbackSubmission).delete()
        db.commit()
        db.close()
    
    def test_create_feedback_submission_complete(self):
        """Test creating a feedback submission with all fields"""
        feedback_data = {
            "n8n_execution_id": "test-execution-123",
            "email": "test@example.com",
            
            # LinkedIn Content
            "linkedin_grok_content": "What if AI could transform prenatal care into a lifeline for millions?",
            "linkedin_o3_content": "What if your next ultrasound could learn from millions of others?",
            "linkedin_gemini_content": "What if every clinician had a co-pilot in the exam room?",
            "linkedin_feedback": "Great content, very engaging!",
            "linkedin_chosen_llm": "Grok",
            "linkedin_custom_content": "Custom LinkedIn post content",
            
            # X Content
            "x_grok_content": "Sample X Grok content",
            "x_o3_content": "Sample X o3 content", 
            "x_gemini_content": "Sample X Gemini content",
            "x_feedback": "X content needs improvement",
            "x_chosen_llm": "Gemini",
            "x_custom_content": "Custom X post content",
            
            # Image URLs
            "stable_diffusion_image_url": "https://example.com/stable-diffusion.jpg",
            "pixabay_image_url": "https://example.com/pixabay.jpg",
            "gpt1_image_url": "https://example.com/gpt1.jpg",
            "image_feedback": "Images look great!",
            "image_chosen_llm": "Stable"
        }
        
        response = client.post("/api/feedback", json=feedback_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check that submission_id is generated
        assert "submission_id" in data
        assert data["submission_id"] is not None
        
        # Check all fields are stored correctly
        assert data["n8n_execution_id"] == "test-execution-123"
        assert data["email"] == "test@example.com"
        assert data["linkedin_grok_content"] == feedback_data["linkedin_grok_content"]
        assert data["linkedin_o3_content"] == feedback_data["linkedin_o3_content"]
        assert data["linkedin_gemini_content"] == feedback_data["linkedin_gemini_content"]
        assert data["linkedin_feedback"] == feedback_data["linkedin_feedback"]
        assert data["linkedin_chosen_llm"] == feedback_data["linkedin_chosen_llm"]
        assert data["linkedin_custom_content"] == feedback_data["linkedin_custom_content"]
        assert data["x_grok_content"] == feedback_data["x_grok_content"]
        assert data["x_o3_content"] == feedback_data["x_o3_content"]
        assert data["x_gemini_content"] == feedback_data["x_gemini_content"]
        assert data["x_feedback"] == feedback_data["x_feedback"]
        assert data["x_chosen_llm"] == feedback_data["x_chosen_llm"]
        assert data["x_custom_content"] == feedback_data["x_custom_content"]
        assert data["stable_diffusion_image_url"] == feedback_data["stable_diffusion_image_url"]
        assert data["pixabay_image_url"] == feedback_data["pixabay_image_url"]
        assert data["gpt1_image_url"] == feedback_data["gpt1_image_url"]
        assert data["image_feedback"] == feedback_data["image_feedback"]
        assert data["image_chosen_llm"] == feedback_data["image_chosen_llm"]
        
        # Check timestamps are created
        assert "created_at" in data
        assert data["created_at"] is not None
    
    def test_create_feedback_submission_minimal(self):
        """Test creating a feedback submission with only required fields"""
        feedback_data = {
            "n8n_execution_id": "minimal-execution-456",
            "email": "minimal@example.com"
        }
        
        response = client.post("/api/feedback", json=feedback_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["n8n_execution_id"] == "minimal-execution-456"
        assert data["email"] == "minimal@example.com"
        assert data["submission_id"] is not None
        
        # Optional fields should be None
        assert data["linkedin_grok_content"] is None
        assert data["x_feedback"] is None
        assert data["image_chosen_llm"] is None
    
    def test_create_feedback_submission_missing_required(self):
        """Test creating a feedback submission without required n8n_execution_id and email"""
        feedback_data = {
            "linkedin_feedback": "This should fail"
        }
        
        response = client.post("/api/feedback", json=feedback_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_get_feedback_by_submission_id(self):
        """Test retrieving a feedback submission by submission ID"""
        # First create a submission
        feedback_data = {
            "n8n_execution_id": "get-test-789",
            "email": "get@example.com",
            "linkedin_feedback": "Test feedback"
        }
        
        create_response = client.post("/api/feedback", json=feedback_data)
        assert create_response.status_code == 200
        
        submission_id = create_response.json()["submission_id"]
        
        # Now retrieve it
        get_response = client.get(f"/api/feedback/{submission_id}")
        assert get_response.status_code == 200
        
        data = get_response.json()
        assert data["n8n_execution_id"] == "get-test-789"
        assert data["linkedin_feedback"] == "Test feedback"
        assert data["submission_id"] == submission_id
    
    def test_get_feedback_by_submission_id_not_found(self):
        """Test retrieving a non-existent feedback submission"""
        response = client.get("/api/feedback/non-existent-id")
        assert response.status_code == 404
    
    def test_get_all_feedback_submissions(self):
        """Test retrieving all feedback submissions"""
        # Create multiple submissions
        feedback_data_1 = {
            "n8n_execution_id": "all-test-1",
            "email": "all1@example.com",
            "linkedin_feedback": "First feedback"
        }
        
        feedback_data_2 = {
            "n8n_execution_id": "all-test-2",
            "email": "all2@example.com",
            "linkedin_feedback": "Second feedback"
        }
        
        client.post("/api/feedback", json=feedback_data_1)
        client.post("/api/feedback", json=feedback_data_2)
        
        # Get all submissions
        response = client.get("/api/feedback")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 2
        
        # Check that both submissions are returned
        execution_ids = [item["n8n_execution_id"] for item in data]
        assert "all-test-1" in execution_ids
        assert "all-test-2" in execution_ids
    
    def test_get_feedback_by_execution_id(self):
        """Test retrieving feedback submissions by n8n execution ID"""
        # Create submissions with same execution ID
        feedback_data_1 = {
            "n8n_execution_id": "execution-123",
            "email": "exec1@example.com",
            "linkedin_feedback": "First feedback for execution-123"
        }
        
        feedback_data_2 = {
            "n8n_execution_id": "execution-123",
            "email": "exec2@example.com",
            "linkedin_feedback": "Second feedback for execution-123"
        }
        
        feedback_data_3 = {
            "n8n_execution_id": "execution-456",
            "email": "exec3@example.com",
            "linkedin_feedback": "Feedback for different execution"
        }
        
        client.post("/api/feedback", json=feedback_data_1)
        client.post("/api/feedback", json=feedback_data_2)
        client.post("/api/feedback", json=feedback_data_3)
        
        # Get feedback for execution-123
        response = client.get("/api/feedback/execution/execution-123")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 2
        
        # Check that only submissions for execution-123 are returned
        for item in data:
            assert item["n8n_execution_id"] == "execution-123"
    
    def test_health_check(self):
        """Test the health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
    
    def test_root_endpoint(self):
        """Test the root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "n8n Execution Feedback API"
        assert data["version"] == "1.0.0" 