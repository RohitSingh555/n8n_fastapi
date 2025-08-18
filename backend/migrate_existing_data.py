#!/usr/bin/env python3
"""
Script to migrate existing data and establish proper relationships between
feedback_submissions and social_media_posts tables.

This script will:
1. Add the feedback_submission_id column to social_media_posts table
2. Link existing social media posts to their corresponding feedback submissions
3. Clean up any orphaned records
"""

import sqlite3
import os
from datetime import datetime

def migrate_existing_data():
    """Migrate existing data to establish proper relationships"""
    
    # Database path
    db_path = "app/n8n_feedback.db"
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return
    
    print(f"Starting migration of existing data...")
    print(f"Database: {db_path}")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if feedback_submission_id column already exists
        cursor.execute("PRAGMA table_info(social_media_posts)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'feedback_submission_id' not in columns:
            print("Adding feedback_submission_id column...")
            cursor.execute("ALTER TABLE social_media_posts ADD COLUMN feedback_submission_id VARCHAR(255)")
            print("Column added successfully")
        else:
            print("feedback_submission_id column already exists")
        
        # Get all feedback submissions and social media posts
        cursor.execute("""
            SELECT submission_id, email, created_at 
            FROM feedback_submissions 
            ORDER BY created_at ASC
        """)
        feedback_submissions = cursor.fetchall()
        
        cursor.execute("""
            SELECT post_id, email, created_at 
            FROM social_media_posts 
            ORDER BY created_at ASC
        """)
        social_media_posts = cursor.fetchall()
        
        print(f"Found {len(feedback_submissions)} feedback submissions")
        print(f"Found {len(social_media_posts)} social media posts")
        
        # Link social media posts to feedback submissions based on email and creation time proximity
        linked_count = 0
        orphaned_count = 0
        
        for post in social_media_posts:
            post_id, post_email, post_created = post
            
            # Find the feedback submission with the same email and closest creation time
            best_match = None
            best_time_diff = float('inf')
            
            for feedback in feedback_submissions:
                feedback_id, feedback_email, feedback_created = feedback
                
                if post_email == feedback_email:
                    # Parse timestamps
                    try:
                        post_time = datetime.fromisoformat(post_created.replace('Z', '+00:00'))
                        feedback_time = datetime.fromisoformat(feedback_created.replace('Z', '+00:00'))
                        
                        # Calculate time difference in seconds
                        time_diff = abs((post_time - feedback_time).total_seconds())
                        
                        if time_diff < best_time_diff:
                            best_time_diff = time_diff
                            best_match = feedback_id
                    except Exception as e:
                        print(f"Error parsing timestamps for post {post_id}: {e}")
                        continue
            
            if best_match and best_time_diff <= 300:  # Within 5 minutes
                # Update the social media post with the feedback submission ID
                cursor.execute("""
                    UPDATE social_media_posts 
                    SET feedback_submission_id = ? 
                    WHERE post_id = ?
                """, (best_match, post_id))
                linked_count += 1
                print(f"Linked post {post_id} to feedback submission {best_match} (time diff: {best_time_diff:.1f}s)")
            else:
                orphaned_count += 1
                print(f"Could not link post {post_id} - no suitable feedback submission found")
        
        # Commit changes
        conn.commit()
        
        print(f"\nMigration completed!")
        print(f"Successfully linked: {linked_count} posts")
        print(f"Orphaned posts: {orphaned_count}")
        
        # Verify the relationships
        cursor.execute("""
            SELECT COUNT(*) FROM social_media_posts 
            WHERE feedback_submission_id IS NOT NULL
        """)
        linked_count_verify = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM social_media_posts 
            WHERE feedback_submission_id IS NULL
        """)
        unlinked_count = cursor.fetchone()[0]
        
        print(f"\nVerification:")
        print(f"Posts with feedback_submission_id: {linked_count_verify}")
        print(f"Posts without feedback_submission_id: {unlinked_count}")
        
        # Show some example relationships
        cursor.execute("""
            SELECT s.post_id, s.feedback_submission_id, s.email, s.created_at as post_created,
                   f.created_at as feedback_created
            FROM social_media_posts s
            LEFT JOIN feedback_submissions f ON s.feedback_submission_id = f.submission_id
            WHERE s.feedback_submission_id IS NOT NULL
            ORDER BY s.created_at DESC
            LIMIT 5
        """)
        
        relationships = cursor.fetchall()
        if relationships:
            print(f"\nExample relationships:")
            for rel in relationships:
                post_id, feedback_id, email, post_created, feedback_created = rel
                print(f"  Post {post_id[:8]}... -> Feedback {feedback_id[:8]}... ({email})")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_existing_data()

