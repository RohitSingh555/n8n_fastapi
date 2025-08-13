"""Initial database schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2025-01-27 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create feedback_submissions table
    op.create_table('feedback_submissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('submission_id', sa.String(255), nullable=False),
        sa.Column('n8n_execution_id', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        
        # LinkedIn Content
        sa.Column('linkedin_grok_content', sa.Text(), nullable=True),
        sa.Column('linkedin_o3_content', sa.Text(), nullable=True),
        sa.Column('linkedin_gemini_content', sa.Text(), nullable=True),
        sa.Column('linkedin_feedback', sa.Text(), nullable=True),
        sa.Column('linkedin_chosen_llm', sa.String(100), nullable=True),
        sa.Column('linkedin_custom_content', sa.Text(), nullable=True),
        
        # X Content
        sa.Column('x_grok_content', sa.Text(), nullable=True),
        sa.Column('x_o3_content', sa.Text(), nullable=True),
        sa.Column('x_gemini_content', sa.Text(), nullable=True),
        sa.Column('x_feedback', sa.Text(), nullable=True),
        sa.Column('x_chosen_llm', sa.String(100), nullable=True),
        sa.Column('x_custom_content', sa.Text(), nullable=True),
        
        # Image URLs
        sa.Column('stable_diffusion_image_url', sa.Text(), nullable=True),
        sa.Column('pixabay_image_url', sa.Text(), nullable=True),
        sa.Column('gpt1_image_url', sa.Text(), nullable=True),
        sa.Column('image_feedback', sa.Text(), nullable=True),
        sa.Column('image_chosen_llm', sa.String(100), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create social_media_posts table
    op.create_table('social_media_posts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('post_id', sa.String(255), nullable=True),
        sa.Column('content_creator', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('social_platform', sa.String(100), nullable=False),
        sa.Column('custom_content', sa.Text(), nullable=True),
        sa.Column('ai_prompt', sa.Text(), nullable=True),
        sa.Column('excluded_llms', sa.Text(), nullable=True),
        sa.Column('post_image_type', sa.String(100), nullable=True),
        sa.Column('image_url', sa.Text(), nullable=True),
        sa.Column('image_file_path', sa.Text(), nullable=True),
        sa.Column('ai_image_style', sa.String(100), nullable=True),
        sa.Column('ai_image_description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create webhook_logs table
    op.create_table('webhook_logs',
        sa.Column('log_id', sa.Integer(), nullable=False),
        sa.Column('webhook_type', sa.String(100), nullable=False),
        sa.Column('payload', sa.Text(), nullable=True),
        sa.Column('response_status', sa.Integer(), nullable=True),
        sa.Column('response_body', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        
        sa.PrimaryKeyConstraint('log_id')
    )
    
    # Create indexes for feedback_submissions
    op.create_index('ix_feedback_submissions_submission_id', 'feedback_submissions', ['submission_id'], unique=True)
    op.create_index('ix_feedback_submissions_execution_id', 'feedback_submissions', ['n8n_execution_id'], unique=False)
    op.create_index('ix_feedback_submissions_email', 'feedback_submissions', ['email'], unique=False)
    op.create_index('ix_feedback_submissions_created_at', 'feedback_submissions', ['created_at'], unique=False)
    
    # Create indexes for social_media_posts
    op.create_index('ix_social_media_posts_id', 'social_media_posts', ['id'], unique=False)
    op.create_index('ix_social_media_posts_post_id', 'social_media_posts', ['post_id'], unique=True)
    
    # Create indexes for webhook_logs
    op.create_index('ix_webhook_logs_webhook_type', 'webhook_logs', ['webhook_type'], unique=False)
    op.create_index('ix_webhook_logs_created_at', 'webhook_logs', ['created_at'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_webhook_logs_created_at', table_name='webhook_logs')
    op.drop_index('ix_webhook_logs_webhook_type', table_name='webhook_logs')
    op.drop_index('ix_social_media_posts_post_id', table_name='social_media_posts')
    op.drop_index('ix_social_media_posts_id', table_name='social_media_posts')
    op.drop_index('ix_feedback_submissions_created_at', table_name='feedback_submissions')
    op.drop_index('ix_feedback_submissions_email', table_name='feedback_submissions')
    op.drop_index('ix_feedback_submissions_execution_id', table_name='feedback_submissions')
    op.drop_index('ix_feedback_submissions_submission_id', table_name='feedback_submissions')
    
    # Drop tables
    op.drop_table('webhook_logs')
    op.drop_table('social_media_posts')
    op.drop_table('feedback_submissions')
