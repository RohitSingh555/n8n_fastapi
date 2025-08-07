#!/usr/bin/env python3
"""
Script to populate the database with sample feedback submissions
"""

import requests
import json
import uuid

# Configuration
BASE_URL = "http://104.131.8.230:8000"
API_URL = f"{BASE_URL}/api/feedback"

def create_sample_submissions():
    """Create sample feedback submissions for testing"""
    
    print("🗄️  Creating sample feedback submissions...")
    
    # Sample submission 1 - Complete data
    submission1 = {
        "n8n_execution_id": "exec-12345-abcde",
        "email": "user1@example.com",
        
        # LinkedIn Content
        "linkedin_grok_content": "What if AI could transform prenatal care into a lifeline for millions?\n\nAt Ultrasound AI, we're making that vision a reality. Our cutting-edge technology empowers healthcare providers with tools to predict and address critical maternal health challenges, ensuring better outcomes for women and families worldwide.\n\nHow do you see AI shaping the future of healthcare? #WomensHealth #AIInnovation #PrenatalCare",
        "linkedin_o3_content": "What if your next ultrasound could learn from millions of others?\n\nAt Ultrasound AI, we train our algorithms on diverse, global datasets so every expecting parent benefits from the most inclusive insights available. By detecting subtle patterns that traditional methods miss, our AI elevates prenatal care from reactive to proactive.\n\nHow is data diversity shaping your approach to innovation? #PrenatalCare #AIInnovation #HealthEquity",
        "linkedin_gemini_content": "What if every clinician had a co-pilot in the exam room?\n\nOur AI is designed to be just that. It analyzes complex data in real-time, flagging potential risks and offering data-driven insights that support clinical decisions. This frees our healthcare heroes to do what they do best: connect with patients and provide compassionate, expert care.\n\nTo all the healthcare providers out there: what's the biggest challenge AI could help you solve? #UltrasoundAI #AIinMedicine #ClinicalSupport",
        "linkedin_feedback": "The Grok content is engaging and professional. Good use of hashtags.",
        "linkedin_chosen_llm": "Grok",
        "linkedin_custom_content": "Custom LinkedIn post with additional insights about AI in healthcare.",
        
        # X Content
        "x_grok_content": "🚀 AI is revolutionizing prenatal care! Our Ultrasound AI technology helps healthcare providers predict and address maternal health challenges. #AI #Healthcare #Innovation",
        "x_o3_content": "💡 What if your ultrasound could learn from millions of others? Our AI uses diverse global datasets to provide inclusive insights for every expecting parent. #PrenatalCare #HealthEquity",
        "x_gemini_content": "👨‍⚕️ Every clinician deserves a co-pilot! Our AI analyzes data in real-time, flagging risks and supporting clinical decisions. #DigitalHealth #PhysicianBurnout",
        "x_feedback": "The X content is concise and impactful. Good use of emojis and hashtags.",
        "x_chosen_llm": "Gemini",
        "x_custom_content": "Custom X post about the future of AI in medical imaging.",
        
        # Image URLs
        "stable_diffusion_image_url": "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=800&h=600&fit=crop",
        "pixabay_image_url": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1f?w=800&h=600&fit=crop",
        "gpt1_image_url": "https://images.unsplash.com/photo-1581595219315-a187dd40c322?w=800&h=600&fit=crop",
        "image_feedback": "The Stable Diffusion image is the most professional and relevant to healthcare.",
        "image_chosen_llm": "Stable"
    }
    
    # Sample submission 2 - Minimal data
    submission2 = {
        "n8n_execution_id": "exec-67890-fghij",
        "email": "user2@example.com",
        
        # LinkedIn Content
        "linkedin_grok_content": "Sample LinkedIn Grok content for testing purposes.",
        "linkedin_o3_content": "Sample LinkedIn o3 content for testing purposes.",
        "linkedin_gemini_content": "Sample LinkedIn Gemini content for testing purposes.",
        "linkedin_feedback": "Need to review all options before deciding.",
        "linkedin_chosen_llm": "",
        "linkedin_custom_content": "",
        
        # X Content
        "x_grok_content": "Sample X Grok content for testing.",
        "x_o3_content": "Sample X o3 content for testing.",
        "x_gemini_content": "Sample X Gemini content for testing.",
        "x_feedback": "Still evaluating the options.",
        "x_chosen_llm": "",
        "x_custom_content": "",
        
        # Image URLs
        "stable_diffusion_image_url": "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=400&h=300&fit=crop",
        "pixabay_image_url": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1f?w=400&h=300&fit=crop",
        "gpt1_image_url": "https://images.unsplash.com/photo-1581595219315-a187dd40c322?w=400&h=300&fit=crop",
        "image_feedback": "Images look good, need to choose one.",
        "image_chosen_llm": ""
    }
    
    # Sample submission 3 - Focus on X content
    submission3 = {
        "n8n_execution_id": "exec-11111-klmno",
        "email": "user3@example.com",
        
        # LinkedIn Content
        "linkedin_grok_content": "LinkedIn content focused on professional networking.",
        "linkedin_o3_content": "LinkedIn content with business insights.",
        "linkedin_gemini_content": "LinkedIn content for industry professionals.",
        "linkedin_feedback": "LinkedIn content is too formal for our audience.",
        "linkedin_chosen_llm": "o3",
        "linkedin_custom_content": "Custom LinkedIn post with more casual tone.",
        
        # X Content
        "x_grok_content": "🔥 Breaking: AI is transforming how we approach prenatal care! Our Ultrasound AI is making waves in the healthcare industry. #AI #Healthcare #Innovation #BreakingNews",
        "x_o3_content": "💪 Empowering healthcare providers with AI! Our technology helps predict maternal health challenges before they become critical. #Empowerment #Healthcare #AI",
        "x_gemini_content": "🎯 Precision meets compassion! Our AI co-pilot supports clinicians with real-time insights while maintaining the human touch in patient care. #Precision #Compassion #Healthcare",
        "x_feedback": "The X content is perfect! Engaging, informative, and uses trending hashtags effectively.",
        "x_chosen_llm": "Grok",
        "x_custom_content": "Custom X thread with additional insights and statistics.",
        
        # Image URLs
        "stable_diffusion_image_url": "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=600&h=400&fit=crop",
        "pixabay_image_url": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1f?w=600&h=400&fit=crop",
        "gpt1_image_url": "https://images.unsplash.com/photo-1581595219315-a187dd40c322?w=600&h=400&fit=crop",
        "image_feedback": "All images are high quality, but the Stable Diffusion one matches our brand best.",
        "image_chosen_llm": "Stable"
    }
    
    submissions = [submission1, submission2, submission3]
    created_ids = []
    
    for i, submission in enumerate(submissions, 1):
        try:
            print(f"\n📝 Creating submission {i}...")
            response = requests.post(API_URL, json=submission)
            response.raise_for_status()
            created_feedback = response.json()
            submission_id = created_feedback["submission_id"]
            created_ids.append(submission_id)
            print(f"✅ Created submission {i} with ID: {submission_id}")
            print(f"   Email: {submission['email']}")
            print(f"   Execution ID: {submission['n8n_execution_id']}")
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to create submission {i}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"   Response: {e.response.text}")
    
    print(f"\n🎉 Created {len(created_ids)} sample submissions!")
    print("\n📋 Sample Submission IDs for testing:")
    for i, submission_id in enumerate(created_ids, 1):
        print(f"   {i}. {submission_id}")
    
    print("\n🔗 You can now test the form by:")
    print("   1. Starting the frontend: cd frontend && npm start")
    print("   2. Starting the backend: cd backend && uvicorn app.main:app --reload")
    print("   3. Entering one of the submission IDs above in the 'Load Existing Feedback' section")
    
    return created_ids

if __name__ == "__main__":
    try:
        created_ids = create_sample_submissions()
        if created_ids:
            print(f"\n✅ Successfully created {len(created_ids)} sample submissions!")
        else:
            print("\n❌ No submissions were created!")
            exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  Script interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        exit(1) 