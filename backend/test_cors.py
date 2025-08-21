#!/usr/bin/env python3
"""
Simple CORS test script to verify the FastAPI server is properly configured
"""

import requests
import json

def test_cors():
    """Test CORS configuration on the FastAPI server"""
    
    # Test URLs
    base_url = "http://104.131.8.230:8000"
    test_endpoints = [
        "/health",
        "/cors-test", 
        "/cors-debug",
        "/test-post",
        "/api/users/login"  # Test the actual login endpoint
    ]
    
    # Test headers that would be sent by a browser
    headers = {
        "Origin": "http://104.131.8.230:3000",
        "User-Agent": "Mozilla/5.0 (Test Browser)",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive"
    }
    
    print("Testing CORS configuration...")
    print(f"Base URL: {base_url}")
    print(f"Origin: {headers['Origin']}")
    print("-" * 50)
    
    for endpoint in test_endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\nTesting endpoint: {endpoint}")
        
        try:
            cors_headers = [
                "Access-Control-Allow-Origin",
                "Access-Control-Allow-Methods", 
                "Access-Control-Allow-Headers",
                "Access-Control-Allow-Credentials",
                "Access-Control-Max-Age"
            ]
            
            # Test GET request for most endpoints
            if endpoint != "/api/users/login":
                response = requests.get(url, headers=headers, timeout=10)
                print(f"  GET Status: {response.status_code}")
                print(f"  CORS Headers:")
                
                for header in cors_headers:
                    value = response.headers.get(header)
                    print(f"    {header}: {value}")
            else:
                # For login endpoint, test POST request with sample data
                login_data = {"username": "test", "password": "test"}
                post_headers = headers.copy()
                post_headers["Content-Type"] = "application/json"
                
                response = requests.post(url, headers=post_headers, json=login_data, timeout=10)
                print(f"  POST Status: {response.status_code}")
                print(f"  CORS Headers:")
                
                for header in cors_headers:
                    value = response.headers.get(header)
                    print(f"    {header}: {value}")
                
                if response.status_code == 401:
                    print(f"    Expected 401 for invalid credentials - CORS working!")
            
            # Test OPTIONS request (preflight) for all endpoints
            print(f"  Testing OPTIONS preflight...")
            preflight_headers = headers.copy()
            preflight_headers["Access-Control-Request-Method"] = "POST"
            preflight_headers["Access-Control-Request-Headers"] = "content-type"
            
            options_response = requests.options(url, headers=preflight_headers, timeout=10)
            print(f"    OPTIONS Status: {options_response.status_code}")
            
            for header in cors_headers:
                value = options_response.headers.get(header)
                print(f"      {header}: {value}")
                
        except requests.exceptions.RequestException as e:
            print(f"  Error: {e}")
    
    print("\n" + "=" * 50)
    print("CORS test completed!")

if __name__ == "__main__":
    test_cors()
