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
    
    def test_escape_characters_in_feedback(self):
        """Test that the API properly handles escape characters in feedback content"""
        feedback_data = {
            "n8n_execution_id": "test-escape-123",
            "email": "test@example.com",
            "linkedin_feedback": "This is a test feedback\nwith a newline\nand another newline",
            "linkedin_chosen_llm": "Grok",
            "x_feedback": "X feedback with\ttab\tcharacters",
            "x_chosen_llm": "Gemini",
            "image_feedback": "Image feedback with\\nliteral backslash+n",
            "image_chosen_llm": "Stable"
        }
        
        response = client.post("/api/feedback", json=feedback_data)
        assert response.status_code == 200
        
        data = response.json()
        submission_id = data["submission_id"]
        
        # Verify the escape characters were stored correctly
        assert "\n" in feedback_data["linkedin_feedback"]
        assert "\t" in feedback_data["x_feedback"]
        assert "\\n" in feedback_data["image_feedback"]
        
        # Retrieve and verify the stored data
        get_response = client.get(f"/api/feedback/{submission_id}")
        assert get_response.status_code == 200
        
        retrieved_data = get_response.json()
        assert retrieved_data["linkedin_feedback"] == feedback_data["linkedin_feedback"]
        assert retrieved_data["x_feedback"] == feedback_data["x_feedback"]
        assert retrieved_data["image_feedback"] == feedback_data["image_feedback"]
        
        # Verify newlines and tabs are preserved
        assert "\n" in retrieved_data["linkedin_feedback"]
        assert "\t" in retrieved_data["x_feedback"]
    
    def test_update_feedback_with_escape_characters(self):
        """Test updating feedback with escape characters"""
        # First create a feedback submission
        feedback_data = {
            "n8n_execution_id": "test-update-escape-123",
            "email": "test@example.com",
            "linkedin_feedback": "Initial feedback",
            "linkedin_chosen_llm": "Grok"
        }
        
        create_response = client.post("/api/feedback", json=feedback_data)
        assert create_response.status_code == 200
        submission_id = create_response.json()["submission_id"]
        
        # Update with escape characters
        update_data = {
            "linkedin_feedback": "Updated feedback\nwith\nmultiple\nnewlines",
            "x_feedback": "Updated X feedback\twith\ttabs\tand\nnewlines",
            "image_feedback": "Updated image feedback with \\\"quotes\\\" and \\\\backslashes\\\\"
        }
        
        update_response = client.put(f"/api/feedback/{submission_id}", json=update_data)
        assert update_response.status_code == 200
        
        updated_data = update_response.json()
        assert updated_data["linkedin_feedback"] == update_data["linkedin_feedback"]
        assert updated_data["x_feedback"] == update_data["x_feedback"]
        assert updated_data["image_feedback"] == update_data["image_feedback"]
        
        # Verify the escape characters are preserved
        assert "\n" in updated_data["linkedin_feedback"]
        assert "\t" in updated_data["image_feedback"]
        assert "\"" in updated_data["image_feedback"]
        assert "\\" in updated_data["image_feedback"]
    
    def test_user_specific_json_data(self):
        """Test the API with the user's specific JSON data containing multiline content"""
        user_data = {
            "n8n_execution_id": "test-user-ultrasound-123",
            "email": "Matthew@AutomationConsultingServices.org",
            "linkedin_grok_content": "Ready to see the future of prenatal care?\n\nAt Ultrasound AI, we're thrilled to showcase how our cutting-edge artificial intelligence is transforming the way clinicians support expectant mothers. By harnessing the power of AI, we're enabling earlier predictions and more personalized care—because every pregnancy journey deserves the best start possible.\n\nOur mission is simple yet profound: to empower healthcare providers with innovative tools that improve outcomes for women and families worldwide. With a focus on accessibility and inclusivity, we're breaking down barriers to ensure that life-changing technology reaches everyone, no matter their location or circumstances.\n\nJoin us in revolutionizing maternal health. How do you envision AI shaping the future of healthcare? Share your thoughts below—we'd love to hear from you! #MaternalHealth #AIInnovation #PrenatalCare #UltrasoundAI #HealthcareTech",
            "linkedin_o3_content": "What if every expectant parent, everywhere, had the same chance at a healthy start?\n\nAt Ultrasound AI, that question drives our work each day. By merging decades of medical expertise with state-of-the-art artificial intelligence, we help clinicians spot risks sooner and tailor care to each pregnancy—no matter the zip code or ability to pay. Our commitment to equitable, impactful, and inclusive innovation means healthier outcomes for women and families worldwide.\n\nImagine a future where personalized prenatal insights are just a scan away. We're building it—together. How do you see AI elevating maternal health in your community? Share below! #PrenatalCare #AIInnovation #WomensHealth #UltrasoundAI",
            "linkedin_gemini_content": "Imagine a world where every pregnancy is supported by the power of AI.\n\nAt Ultrasound AI, we're turning that vision into reality. Our technology empowers healthcare providers with deeper insights, helping them deliver more personalized and proactive care to expectant mothers. We believe in the power of innovation to create better outcomes.\n\nOur work is driven by a simple, powerful goal: to advance women's health with accessible and impactful solutions. By designing our technology with diverse data, we ensure that every family, everywhere, can benefit from a healthier start.\n\nWhat's one way you've seen technology improve patient care? Let's celebrate the progress. #UltrasoundAI #AIinHealthcare #PrenatalCare #WomensHealth #HealthTech #Innovation",
            "linkedin_feedback": "",
            "linkedin_chosen_llm": "",
            "linkedin_custom_content": "",
            "x_grok_content": "Write me a X/Twitter post that follows the user's message (<UserMessage>) below. If there is any feedback in the <feedback> section you are to pay very close attention to it. If there is any <feedback> available related to previous posts about the <UserMessage> which are stored in your memory make sure to take those into careful consideration before generating a new response.",
            "x_o3_content": "Write me a X/Twitter post that follows the user's message (<UserMessage>) below. If there is any feedback in the <feedback> section you are to pay very close attention to it. If there is any <feedback> available related to previous posts about the <UserMessage> which are stored in your memory make sure to take those into careful consideration before generating a new response.",
            "x_gemini_content": "Write me a X/Twitter post that follows the user's message (<UserMessage>) below. If there is any feedback in the <feedback> section you are to pay very close attention to it. If there is any <feedback> available related to previous posts about the <UserMessage> which are stored in your memory make sure to take those into careful consideration before generating a new response.",
            "x_feedback": "string",
            "x_chosen_llm": "string",
            "x_custom_content": "string",
            "stable_diffusion_image_url": "string",
            "pixabay_image_url": "string",
            "gpt1_image_url": "string",
            "image_feedback": "string",
            "image_chosen_llm": "string"
        }
        
        # Count newlines in content fields
        content_fields = ['linkedin_grok_content', 'linkedin_o3_content', 'linkedin_gemini_content']
        total_newlines = sum(user_data[field].count('\n') for field in content_fields if user_data[field])
        
        response = client.post("/api/feedback", json=user_data)
        assert response.status_code == 200
        
        data = response.json()
        submission_id = data["submission_id"]
        
        # Verify the submission was created successfully
        assert "submission_id" in data
        assert data["email"] == "Matthew@AutomationConsultingServices.org"
        
        # Retrieve and verify the stored data
        get_response = client.get(f"/api/feedback/{submission_id}")
        assert get_response.status_code == 200
        
        retrieved_data = get_response.json()
        
        # Verify newlines are preserved in content fields
        for field in content_fields:
            if retrieved_data[field]:
                newline_count = retrieved_data[field].count('\\n')
                assert newline_count > 0, f"Field {field} should contain newlines"
                assert retrieved_data[field] == user_data[field], f"Field {field} content not preserved correctly"
        
        # Verify the total newline count matches
        retrieved_newlines = sum(retrieved_data[field].count('\\n') for field in content_fields if retrieved_data[field])
        assert retrieved_newlines == total_newlines, "Total newline count should be preserved"
    
    def test_escape_character_test_endpoint(self):
        """Test the escape character test endpoint"""
        test_data = {
            "simple_text": "This is simple text",
            "text_with_newlines": "Line 1\\nLine 2\\nLine 3",
            "text_with_tabs": "Column1\\tColumn2\\tColumn3",
            "text_with_quotes": "Text with \\\"quotes\\\" and 'apostrophes'",
            "text_with_backslashes": "Path: C:\\\\Users\\\\Username\\\\Documents",
            "text_with_unicode": "Hello\\u0041\\u0042\\u0043",  # ABC
            "text_with_mixed": "Mixed\\n\\t\\\"content\\nwith\\tescapes",
            "empty_string": "",
            "null_value": None
        }
        
        response = client.post("/api/test-escape-characters", json=test_data)
        assert response.status_code == 200
        
        result = response.json()
        assert "message" in result
        assert "original_data" in result
        assert "processed_data" in result
        assert "escape_character_summary" in result
        
        # Verify the summary
        summary = result["escape_character_summary"]
        assert summary["total_fields"] == 9
        assert summary["string_fields"] == 8  # null_value is not a string
        assert summary["fields_with_escapes"] > 0
        
        # Verify processed data contains escape characters
        processed = result["processed_data"]
        assert processed["text_with_newlines"] == test_data["text_with_newlines"]
        assert processed["text_with_tabs"] == test_data["text_with_tabs"]
        assert processed["text_with_quotes"] == test_data["text_with_quotes"]
        assert processed["text_with_backslashes"] == test_data["text_with_backslashes"] 

class TestWebhookProxy:
    """Test cases for the webhook proxy endpoint"""
    
    def setup_method(self):
        """Setup method to clear database before each test"""
        db = TestingSessionLocal()
        db.query(FeedbackSubmission).delete()
        db.commit()
        db.close()
    
    def test_webhook_proxy_with_image_url(self):
        """Test webhook proxy with external image URL"""
        webhook_data = [{
            "Timestamp": "2024-01-01 12:00:00",
            "Social Platforms": "linkedin",
            "Custom Content?": "Test custom content",
            "AI Prompted Text Generation": "Test AI prompt",
            "Exclude LLMs": "Gemini, o3",
            "Post Image?": "Yes, I have an image URL",
            "Upload an Image": "",
            "Image URL": "https://example.com/test-image.jpg",
            "Content Creator": "test@example.com"
        }]
        
        response = client.post("/api/webhook-proxy", json=webhook_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "feedback_form_link" in data
        assert "feedback_submission_id" in data
        assert "social_media_post_id" in data
        
        # Verify the social media post was created with correct image URL
        post_id = data["social_media_post_id"]
        get_response = client.get(f"/api/social-media-posts/{post_id}")
        assert get_response.status_code == 200
        
        post_data = get_response.json()
        assert post_data["post_image_type"] == "Yes, Image URL"
        assert post_data["image_url"] == "https://example.com/test-image.jpg"
        assert post_data["uploaded_image_url"] is None
    
    def test_webhook_proxy_with_uploaded_image(self):
        """Test webhook proxy with uploaded image URL"""
        webhook_data = [{
            "Timestamp": "2024-01-01 12:00:00",
            "Social Platforms": "twitter",
            "Custom Content?": "Test custom content",
            "AI Prompted Text Generation": "Test AI prompt",
            "Exclude LLMs": "Grok",
            "Post Image?": "Yes, I have an image upload",
            "Upload an Image": "https://example.com/uploaded-image.jpg",
            "Image URL": "",
            "Content Creator": "test@example.com"
        }]
        
        response = client.post("/api/webhook-proxy", json=webhook_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "feedback_form_link" in data
        assert "feedback_submission_id" in data
        assert "social_media_post_id" in data
        
        # Verify the social media post was created with correct uploaded image URL
        post_id = data["social_media_post_id"]
        get_response = client.get(f"/api/social-media-posts/{post_id}")
        assert get_response.status_code == 200
        
        post_data = get_response.json()
        assert post_data["post_image_type"] == "Yes, Upload Image"
        assert post_data["uploaded_image_url"] == "https://example.com/uploaded-image.jpg"
        assert post_data["image_url"] is None
    
    def test_webhook_proxy_with_ai_generated_image(self):
        """Test webhook proxy with AI generated image option"""
        webhook_data = [{
            "Timestamp": "2024-01-01 12:00:00",
            "Social Platforms": "linkedin",
            "Custom Content?": "Test custom content",
            "AI Prompted Text Generation": "Test AI prompt",
            "Exclude LLMs": "",
            "Post Image?": "Yes, AI generated image",
            "Upload an Image": "",
            "Image URL": "",
            "Content Creator": "test@example.com"
        }]
        
        response = client.post("/api/webhook-proxy", json=webhook_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "feedback_form_link" in data
        assert "feedback_submission_id" in data
        assert "social_media_post_id" in data
        
        # Verify the social media post was created with no image URLs
        post_id = data["social_media_post_id"]
        get_response = client.get(f"/api/social-media-posts/{post_id}")
        assert get_response.status_code == 200
        
        post_data = get_response.json()
        assert post_data["post_image_type"] == "Yes, AI Generated"
        assert post_data["image_url"] is None
        assert post_data["uploaded_image_url"] is None 