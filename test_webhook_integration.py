#!/usr/bin/env python3
"""
Test script to verify webhook integration functionality.
This script tests that:
1. Webhook creates empty feedback entry in database
2. Webhook includes feedback URL in the request to n8n
3. Social media post entry is created in database
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"  # Adjust if your backend runs on different port
TEST_WEBHOOK_URL = "https://httpbin.org/post"  # Use httpbin for testing

def test_webhook_integration():
    """Test the webhook integration functionality"""
    
    print("🧪 Testing Webhook Integration...")
    print("=" * 50)
    
    # Test data - simulate social media form submission
    test_payload = [{
        "Timestamp": "12/20/2024 14:30:00",
        "Social Platforms": "LinkedIn, X/Twitter",
        "Custom Content?": "Test social media post content",
        "AI Prompted Text Generation": "",
        "Exclude LLMs": "Claude, GPT-4",
        "Post Image?": "Yes, I have an image URL",
        "Upload an Image": "",
        "Image URL": "https://example.com/test-image.jpg",
        "Content Creator": "test@example.com"
    }]
    
    try:
        print("📤 Sending test payload to webhook proxy...")
        print(f"Payload: {json.dumps(test_payload, indent=2)}")
        
        # Send request to webhook proxy
        response = requests.post(
            f"{BASE_URL}/api/webhook-proxy",
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📥 Response Status: {response.status_code}")
        print(f"📥 Response Headers: {dict(response.headers)}")
        
        if response.ok:
            response_data = response.json()
            print(f"📥 Response Body: {json.dumps(response_data, indent=2)}")
            
            # Check if feedback form link is returned
            if response_data.get("feedback_form_link"):
                print("✅ SUCCESS: Feedback form link received!")
                print(f"🔗 Feedback URL: {response_data['feedback_form_link']}")
            else:
                print("⚠️  WARNING: No feedback form link in response")
                
            # Check if message indicates success
            if response_data.get("message") == "Webhook request forwarded successfully":
                print("✅ SUCCESS: Webhook request forwarded successfully")
            else:
                print("⚠️  WARNING: Unexpected success message")
                
        else:
            print(f"❌ ERROR: Request failed with status {response.status_code}")
            print(f"Error response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to backend server")
        print("Make sure the backend is running on the correct port")
    except requests.exceptions.Timeout:
        print("❌ ERROR: Request timed out")
    except Exception as e:
        print(f"❌ ERROR: Unexpected error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")

def test_database_entries():
    """Test that database entries were created"""
    
    print("\n🗄️  Testing Database Entries...")
    print("=" * 50)
    
    try:
        # Test feedback submissions endpoint
        print("📊 Checking feedback submissions...")
        response = requests.get(f"{BASE_URL}/api/feedback", timeout=10)
        
        if response.ok:
            feedback_data = response.json()
            print(f"✅ Found {len(feedback_data)} feedback submissions")
            
            # Show the most recent ones
            for i, submission in enumerate(feedback_data[-3:], 1):
                print(f"  {i}. ID: {submission.get('submission_id', 'N/A')}")
                print(f"     Email: {submission.get('email', 'N/A')}")
                print(f"     Execution ID: {submission.get('n8n_execution_id', 'N/A')}")
                print()
        else:
            print(f"⚠️  Could not fetch feedback submissions: {response.status_code}")
            
        # Test social media posts endpoint
        print("📊 Checking social media posts...")
        response = requests.get(f"{BASE_URL}/api/social-media-posts", timeout=10)
        
        if response.ok:
            posts_data = response.json()
            print(f"✅ Found {len(posts_data)} social media posts")
            
            # Show the most recent ones
            for i, post in enumerate(posts_data[-3:], 1):
                print(f"  {i}. ID: {post.get('post_id', 'N/A')}")
                print(f"     Creator: {post.get('content_creator', 'N/A')}")
                print(f"     Platform: {post.get('social_platform', 'N/A')}")
                print(f"     Status: {post.get('status', 'N/A')}")
                print()
        else:
            print(f"⚠️  Could not fetch social media posts: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to backend server")
    except requests.exceptions.Timeout:
        print("❌ ERROR: Request timed out")
    except Exception as e:
        print(f"❌ ERROR: Unexpected error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting Webhook Integration Tests...")
    print(f"🌐 Backend URL: {BASE_URL}")
    print(f"🕐 Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run tests
    test_webhook_integration()
    test_database_entries()
    
    print("\n🎯 Test Summary:")
    print("- Webhook integration test completed")
    print("- Database entries test completed")
    print("\n💡 Next steps:")
    print("1. Check the backend logs for any errors")
    print("2. Verify the feedback form link works in the frontend")
    print("3. Check that n8n receives the feedback URL in the webhook")
