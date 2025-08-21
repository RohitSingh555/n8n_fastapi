#!/usr/bin/env python3
"""
Simple CORS test for login endpoint
"""

import requests
import json

def test_login_cors():
    """Test CORS on the login endpoint"""
    
    url = "http://104.131.8.230:8000/api/users/login"
    
    # Test headers that would be sent by a browser
    headers = {
        "Origin": "http://104.131.8.230:3000",
        "User-Agent": "Mozilla/5.0 (Test Browser)",
        "Content-Type": "application/json"
    }
    
    print("Testing CORS on login endpoint...")
    print(f"URL: {url}")
    print(f"Origin: {headers['Origin']}")
    print("-" * 50)
    
    try:
        # Test OPTIONS request (preflight)
        print("1. Testing OPTIONS preflight...")
        options_response = requests.options(url, headers=headers, timeout=10)
        print(f"   Status: {options_response.status_code}")
        
        cors_headers = [
            "Access-Control-Allow-Origin",
            "Access-Control-Allow-Methods", 
            "Access-Control-Allow-Headers",
            "Access-Control-Allow-Credentials",
            "Access-Control-Max-Age"
        ]
        
        print("   CORS Headers:")
        for header in cors_headers:
            value = options_response.headers.get(header)
            print(f"     {header}: {value}")
        
        # Test POST request
        print("\n2. Testing POST request...")
        login_data = {"username": "test", "password": "test"}
        post_response = requests.post(url, headers=headers, json=login_data, timeout=10)
        print(f"   Status: {post_response.status_code}")
        
        print("   CORS Headers:")
        for header in cors_headers:
            value = post_response.headers.get(header)
            print(f"     {header}: {value}")
        
        if post_response.status_code == 401:
            print("   ✅ Expected 401 for invalid credentials - CORS is working!")
        else:
            print(f"   Response body: {post_response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 50)
    print("CORS test completed!")

if __name__ == "__main__":
    test_login_cors()
