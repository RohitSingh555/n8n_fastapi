"""Add separate image LLM fields for Twitter and LinkedIn

Revision ID: 002_add_separate_image_llm_fields
Revises: 001_initial_schema
Create Date: 2025-01-27 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_add_separate_image_llm_fields'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add separate image LLM selection fields for LinkedIn and Twitter
    op.add_column('feedback_submissions', sa.Column('linkedin_image_llm', sa.String(100), nullable=True))
    op.add_column('feedback_submissions', sa.Column('twitter_image_llm', sa.String(100), nullable=True))
    
    # Add separate image LLM selection fields for social_media_posts table
    op.add_column('social_media_posts', sa.Column('linkedin_image_llm', sa.String(100), nullable=True))
    op.add_column('social_media_posts', sa.Column('twitter_image_llm', sa.String(100), nullable=True))
    
    # Create indexes for the new fields
    op.create_index('ix_feedback_submissions_linkedin_image_llm', 'feedback_submissions', ['linkedin_image_llm'], unique=False)
    op.create_index('ix_feedback_submissions_twitter_image_llm', 'feedback_submissions', ['twitter_image_llm'], unique=False)
    op.create_index('ix_social_media_posts_linkedin_image_llm', 'social_media_posts', ['linkedin_image_llm'], unique=False)
    op.create_index('ix_social_media_posts_twitter_image_llm', 'social_media_posts', ['twitter_image_llm'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_social_media_posts_twitter_image_llm', table_name='social_media_posts')
    op.drop_index('ix_social_media_posts_linkedin_image_llm', table_name='social_media_posts')
    op.drop_index('ix_feedback_submissions_twitter_image_llm', table_name='feedback_submissions')
    op.drop_index('ix_feedback_submissions_linkedin_image_llm', table_name='feedback_submissions')
    
    # Drop columns from social_media_posts
    op.drop_column('social_media_posts', 'twitter_image_llm')
    op.drop_column('social_media_posts', 'linkedin_image_llm')
    
    # Drop columns from feedback_submissions
    op.drop_column('feedback_submissions', 'twitter_image_llm')
    op.drop_column('feedback_submissions', 'linkedin_image_llm') 