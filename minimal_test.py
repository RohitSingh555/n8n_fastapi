#!/usr/bin/env python3
"""
Minimal test to check FastAPI app
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"

def test_minimal():
    """Test minimal endpoints"""
    
    print("🧪 Testing minimal endpoints...")
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Root endpoint
    print("\n2. Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Try to access the API docs
    print("\n3. Testing API docs...")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print(f"   Status: {response.status_code}")
        print(f"   Response length: {len(response.text)}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Try to access OpenAPI schema
    print("\n4. Testing OpenAPI schema...")
    try:
        response = requests.get(f"{BASE_URL}/openapi.json")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            schema = response.json()
            paths = schema.get('paths', {})
            print(f"   Available paths: {list(paths.keys())}")
        else:
            print(f"   Error Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_minimal() 