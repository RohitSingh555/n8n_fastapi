#!/usr/bin/env python3
"""
Test script for Social Media API endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_create_social_media_post():
    """Test creating a social media post"""
    print("Testing create social media post...")
    
    post_data = {
        "content_creator": "creator1",
        "email": "Bob@Ultrasound.AI",
        "social_platform": "linkedin",
        "custom_content": "This is a test post content",
        "ai_prompt": "Create a professional LinkedIn post about AI",
        "excluded_llms": "['grok', 'o3']",
        "post_image_type": "ai-generated",
        "ai_image_style": "Realistic",
        "ai_image_description": "Professional business setting",
        "status": "pending"
    }
    
    response = requests.post(f"{BASE_URL}/api/social-media-posts", json=post_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Created post with ID: {result['post_id']}")
        return result['post_id']
    else:
        print(f"Error: {response.text}")
        return None

def test_get_all_posts():
    """Test getting all social media posts"""
    print("Testing get all social media posts...")
    response = requests.get(f"{BASE_URL}/api/social-media-posts")
    print(f"Status: {response.status_code}")
    posts = response.json()
    print(f"Found {len(posts)} posts")
    for post in posts:
        print(f"  - {post['post_id']}: {post['content_creator']} -> {post['social_platform']}")
    print()

def test_get_post_by_id(post_id):
    """Test getting a specific post by ID"""
    print(f"Testing get post by ID: {post_id}...")
    response = requests.get(f"{BASE_URL}/api/social-media-posts/{post_id}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        post = response.json()
        print(f"Post: {post['content_creator']} -> {post['social_platform']}")
    else:
        print(f"Error: {response.text}")
    print()

def test_get_posts_by_creator(creator_id):
    """Test getting posts by creator"""
    print(f"Testing get posts by creator: {creator_id}...")
    response = requests.get(f"{BASE_URL}/api/social-media-posts/creator/{creator_id}")
    print(f"Status: {response.status_code}")
    posts = response.json()
    print(f"Found {len(posts)} posts for creator {creator_id}")
    print()

def test_update_post(post_id):
    """Test updating a post"""
    print(f"Testing update post: {post_id}...")
    
    update_data = {
        "status": "processing",
        "custom_content": "Updated test post content"
    }
    
    response = requests.put(f"{BASE_URL}/api/social-media-posts/{post_id}", json=update_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        post = response.json()
        print(f"Updated post status to: {post['status']}")
    else:
        print(f"Error: {response.text}")
    print()

def test_delete_post(post_id):
    """Test deleting a post"""
    print(f"Testing delete post: {post_id}...")
    response = requests.delete(f"{BASE_URL}/api/social-media-posts/{post_id}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("Post deleted successfully")
    else:
        print(f"Error: {response.text}")
    print()

def main():
    """Run all tests"""
    print("=== Social Media API Test Suite ===\n")
    
    # Test health endpoint
    test_health()
    
    # Test get all posts (should be empty initially)
    test_get_all_posts()
    
    # Test create post
    post_id = test_create_social_media_post()
    
    if post_id:
        # Test get all posts (should have one now)
        test_get_all_posts()
        
        # Test get post by ID
        test_get_post_by_id(post_id)
        
        # Test get posts by creator
        test_get_posts_by_creator("creator1")
        
        # Test update post
        test_update_post(post_id)
        
        # Test delete post
        test_delete_post(post_id)
        
        # Test get all posts (should be empty again)
        test_get_all_posts()
    
    print("=== Test Suite Complete ===")

if __name__ == "__main__":
    main()
