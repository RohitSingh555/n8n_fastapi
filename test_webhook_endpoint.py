#!/usr/bin/env python3
"""
Test script for the new feedback webhook endpoint
"""

import requests
import json
import sys

def test_webhook_endpoint():
    """Test the new feedback webhook endpoint"""
    
    # Test data - simulate a feedback submission
    test_data = {
        "submission_id": "test-submission-123"
    }
    
    # Test the endpoint
    url = "http://localhost:8000/api/submit-feedback-webhook"
    
    print(f"Testing webhook endpoint: {url}")
    print(f"Test data: {json.dumps(test_data, indent=2)}")
    print("-" * 50)
    
    try:
        response = requests.post(
            url,
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.headers.get("content-type", "").startswith("application/json"):
            try:
                response_data = response.json()
                print(f"Response Body: {json.dumps(response_data, indent=2)}")
            except json.JSONDecodeError:
                print(f"Response Body (raw): {response.text}")
        else:
            print(f"Response Body: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the backend server is running on localhost:8000")
        print("   You can start it with: docker compose up backend")
        return False
    except requests.exceptions.Timeout:
        print("❌ Timeout Error: Request took too long")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")
        return False
    
    if response.status_code == 200:
        print("\n✅ Webhook endpoint test successful!")
        return True
    else:
        print(f"\n❌ Webhook endpoint test failed with status {response.status_code}")
        return False

def test_with_real_submission_id():
    """Test with a real submission ID from the database"""
    
    print("\n" + "=" * 60)
    print("Testing with real submission ID from database...")
    print("=" * 60)
    
    # First, get a list of feedback submissions
    try:
        response = requests.get("http://localhost:8000/api/feedback", timeout=10)
        if response.status_code == 200:
            submissions = response.json()
            if submissions:
                # Use the first submission ID
                real_submission_id = submissions[0]["submission_id"]
                print(f"Using real submission ID: {real_submission_id}")
                
                test_data = {"submission_id": real_submission_id}
                response = requests.post(
                    "http://localhost:8000/api/submit-feedback-webhook",
                    json=test_data,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                print(f"Response Status: {response.status_code}")
                if response.status_code == 200:
                    result = response.json()
                    print("✅ Webhook submission successful!")
                    print(f"Message: {result.get('message')}")
                    print(f"Status Code: {result.get('status_code')}")
                else:
                    print(f"❌ Webhook submission failed: {response.status_code}")
                    print(f"Error: {response.text}")
            else:
                print("No feedback submissions found in database")
        else:
            print(f"Failed to get feedback submissions: {response.status_code}")
    except Exception as e:
        print(f"Error testing with real submission ID: {str(e)}")

if __name__ == "__main__":
    print("🧪 Testing Feedback Webhook Endpoint")
    print("=" * 60)
    
    # Test with dummy data first
    success = test_webhook_endpoint()
    
    if success:
        # If successful, test with real data
        test_with_real_submission_id()
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)
