#!/usr/bin/env python3
"""
Simple test script to check API endpoints
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8001"

def test_api_endpoints():
    """Test the API endpoints"""
    
    print("🧪 Testing API endpoints...")
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Root endpoint
    print("\n2. Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: POST feedback endpoint
    print("\n3. Testing POST feedback endpoint...")
    test_data = {
        "n8n_execution_id": "test-exec-123",
        "email": "test@example.com",
        "linkedin_feedback": "Test feedback",
        "linkedin_chosen_llm": "Grok"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/feedback", json=test_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        else:
            print(f"   Error Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: GET all feedback
    print("\n4. Testing GET all feedback...")
    try:
        response = requests.get(f"{BASE_URL}/api/feedback")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Found {len(data)} feedback submissions")
            if data:
                print(f"   First submission ID: {data[0].get('submission_id', 'N/A')}")
        else:
            print(f"   Error Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_api_endpoints() 