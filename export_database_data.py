#!/usr/bin/env python3
"""
Database Export Script
Exports the last 20 entries from each table to an Excel file
"""

import pandas as pd
import pymysql
from sqlalchemy import create_engine, text
from datetime import datetime
import os

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'n8n_user',
    'password': 'n8n_password',
    'database': 'n8n_feedback'
}

def connect_to_database():
    """Connect to the database using PyMySQL"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        print("✅ Successfully connected to database")
        return connection
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        return None

def get_table_counts(connection):
    """Get the count of entries in each table"""
    try:
        with connection.cursor() as cursor:
            # Get count for feedback_submissions
            cursor.execute("SELECT COUNT(*) FROM feedback_submissions")
            feedback_count = cursor.fetchone()[0]
            
            # Get count for social_media_posts
            cursor.execute("SELECT COUNT(*) FROM social_media_posts")
            social_count = cursor.fetchone()[0]
            
            print(f"📊 Table counts:")
            print(f"   - feedback_submissions: {feedback_count} entries")
            print(f"   - social_media_posts: {social_count} entries")
            
            return feedback_count, social_count
    except Exception as e:
        print(f"❌ Error getting table counts: {e}")
        return 0, 0

def export_feedback_submissions(connection, limit=20):
    """Export last N feedback submissions"""
    try:
        query = f"""
        SELECT 
            id,
            submission_id,
            n8n_execution_id,
            email,
            linkedin_grok_content,
            linkedin_o3_content,
            linkedin_gemini_content,
            linkedin_feedback,
            linkedin_chosen_llm,
            linkedin_custom_content,
            x_grok_content,
            x_o3_content,
            x_gemini_content,
            x_feedback,
            x_chosen_llm,
            x_custom_content,
            stable_diffusion_image_url,
            pixabay_image_url,
            gpt1_image_url,
            image_feedback,
            image_chosen_llm,
            created_at,
            updated_at
        FROM feedback_submissions 
        ORDER BY created_at DESC 
        LIMIT {limit}
        """
        
        df = pd.read_sql(query, connection)
        print(f"✅ Exported {len(df)} feedback submissions")
        return df
    except Exception as e:
        print(f"❌ Error exporting feedback submissions: {e}")
        return pd.DataFrame()

def export_social_media_posts(connection, limit=20):
    """Export last N social media posts"""
    try:
        query = f"""
        SELECT 
            id,
            post_id,
            content_creator,
            email,
            social_platform,
            custom_content,
            ai_prompt,
            excluded_llms,
            post_image_type,
            image_url,
            image_file_path,
            ai_image_style,
            ai_image_description,
            status,
            created_at,
            updated_at
        FROM social_media_posts 
        ORDER BY created_at DESC 
        LIMIT {limit}
        """
        
        df = pd.read_sql(query, connection)
        print(f"✅ Exported {len(df)} social media posts")
        return df
    except Exception as e:
        print(f"❌ Error exporting social media posts: {e}")
        return pd.DataFrame()

def create_excel_report(feedback_df, social_df):
    """Create Excel report with multiple sheets"""
    try:
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"database_export_{timestamp}.xlsx"
        
        # Create Excel writer
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Write feedback submissions
            if not feedback_df.empty:
                feedback_df.to_excel(writer, sheet_name='Feedback_Submissions', index=False)
                print(f"📝 Wrote feedback submissions to sheet 'Feedback_Submissions'")
            
            # Write social media posts
            if not social_df.empty:
                social_df.to_excel(writer, sheet_name='Social_Media_Posts', index=False)
                print(f"📝 Wrote social media posts to sheet 'Social_Media_Posts'")
            
            # Create summary sheet
            summary_data = {
                'Metric': [
                    'Total Feedback Submissions',
                    'Total Social Media Posts',
                    'Export Date',
                    'Export Time'
                ],
                'Value': [
                    len(feedback_df),
                    len(social_df),
                    datetime.now().strftime("%Y-%m-%d"),
                    datetime.now().strftime("%H:%M:%S")
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            print(f"📝 Wrote summary to sheet 'Summary'")
        
        print(f"🎉 Excel report created successfully: {filename}")
        return filename
    except Exception as e:
        print(f"❌ Error creating Excel report: {e}")
        return None

def main():
    """Main function to run the export"""
    print("🚀 Starting database export...")
    print("=" * 50)
    
    # Connect to database
    connection = connect_to_database()
    if not connection:
        return
    
    try:
        # Get table counts
        feedback_count, social_count = get_table_counts(connection)
        
        if feedback_count == 0 and social_count == 0:
            print("⚠️  No data found in any table")
            return
        
        print("\n📤 Exporting data...")
        
        # Export data from each table
        feedback_df = export_feedback_submissions(connection, limit=20)
        social_df = export_social_media_posts(connection, limit=20)
        
        # Create Excel report
        if not feedback_df.empty or not social_df.empty:
            filename = create_excel_report(feedback_df, social_df)
            if filename:
                print(f"\n📁 Report saved as: {filename}")
                print(f"📂 Full path: {os.path.abspath(filename)}")
        else:
            print("❌ No data was exported")
            
    except Exception as e:
        print(f"❌ Error during export: {e}")
    finally:
        connection.close()
        print("🔌 Database connection closed")

if __name__ == "__main__":
    main()
