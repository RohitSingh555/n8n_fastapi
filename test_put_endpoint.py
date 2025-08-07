#!/usr/bin/env python3
"""
Test script for the PUT endpoint
"""

import requests
import json
import uuid

# Configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/feedback"

def test_put_endpoint():
    """Test the PUT endpoint functionality"""
    
    print("🧪 Testing PUT endpoint for feedback updates...")
    
    # Step 1: Create a new feedback submission
    print("\n1. Creating a new feedback submission...")
    
    new_feedback = {
        "n8n_execution_id": f"test-exec-{uuid.uuid4().hex[:8]}",
        "email": "test@example.com",
        "linkedin_feedback": "Initial feedback",
        "linkedin_chosen_llm": "Grok",
        "x_feedback": "Initial X feedback",
        "x_chosen_llm": "Gemini",
        "image_feedback": "Initial image feedback",
        "image_chosen_llm": "Stable"
    }
    
    try:
        response = requests.post(API_URL, json=new_feedback)
        response.raise_for_status()
        created_feedback = response.json()
        submission_id = created_feedback["submission_id"]
        print(f"✅ Created feedback with ID: {submission_id}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to create feedback: {e}")
        return False
    
    # Step 2: Update the feedback using PUT
    print("\n2. Updating the feedback submission...")
    
    update_data = {
        "linkedin_feedback": "Updated LinkedIn feedback",
        "linkedin_chosen_llm": "o3",
        "x_feedback": "Updated X feedback",
        "x_chosen_llm": "Grok",
        "image_feedback": "Updated image feedback",
        "image_chosen_llm": "Pixabay"
    }
    
    try:
        response = requests.put(f"{API_URL}/{submission_id}", json=update_data)
        response.raise_for_status()
        updated_feedback = response.json()
        print(f"✅ Updated feedback successfully")
        
        # Verify the updates
        assert updated_feedback["linkedin_feedback"] == "Updated LinkedIn feedback"
        assert updated_feedback["linkedin_chosen_llm"] == "o3"
        assert updated_feedback["x_feedback"] == "Updated X feedback"
        assert updated_feedback["x_chosen_llm"] == "Grok"
        assert updated_feedback["image_feedback"] == "Updated image feedback"
        assert updated_feedback["image_chosen_llm"] == "Pixabay"
        assert updated_feedback["updated_at"] is not None
        
        print("✅ All fields updated correctly")
        print(f"✅ Updated timestamp: {updated_feedback['updated_at']}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to update feedback: {e}")
        return False
    except AssertionError as e:
        print(f"❌ Update verification failed: {e}")
        return False
    
    # Step 3: Test partial update (only some fields)
    print("\n3. Testing partial update...")
    
    partial_update = {
        "linkedin_feedback": "Partially updated feedback"
    }
    
    try:
        response = requests.put(f"{API_URL}/{submission_id}", json=partial_update)
        response.raise_for_status()
        partially_updated = response.json()
        
        # Verify only the specified field was updated
        assert partially_updated["linkedin_feedback"] == "Partially updated feedback"
        assert partially_updated["x_feedback"] == "Updated X feedback"  # Should remain unchanged
        assert partially_updated["image_feedback"] == "Updated image feedback"  # Should remain unchanged
        
        print("✅ Partial update works correctly")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to perform partial update: {e}")
        return False
    except AssertionError as e:
        print(f"❌ Partial update verification failed: {e}")
        return False
    
    # Step 4: Test updating non-existent feedback
    print("\n4. Testing update of non-existent feedback...")
    
    fake_id = "non-existent-id"
    try:
        response = requests.put(f"{API_URL}/{fake_id}", json=update_data)
        if response.status_code == 404:
            print("✅ Correctly returned 404 for non-existent feedback")
        else:
            print(f"❌ Expected 404, got {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error testing non-existent feedback: {e}")
        return False
    
    print("\n🎉 All PUT endpoint tests passed!")
    return True

if __name__ == "__main__":
    try:
        success = test_put_endpoint()
        if success:
            print("\n✅ PUT endpoint is working correctly!")
        else:
            print("\n❌ PUT endpoint tests failed!")
            exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        exit(1) 