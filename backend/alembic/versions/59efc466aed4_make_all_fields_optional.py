"""make_all_fields_optional

Revision ID: 59efc466aed4
Revises: 001_initial_schema
Create Date: 2025-08-13 11:18:55.526260

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '59efc466aed4'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Make all required fields nullable in feedback_submissions table
    op.alter_column('feedback_submissions', 'n8n_execution_id',
                    existing_type=sa.String(255),
                    nullable=True)
    op.alter_column('feedback_submissions', 'email',
                    existing_type=sa.String(255),
                    nullable=True)
    
    # Make all required fields nullable in social_media_posts table
    op.alter_column('social_media_posts', 'content_creator',
                    existing_type=sa.String(255),
                    nullable=True)
    op.alter_column('social_media_posts', 'email',
                    existing_type=sa.String(255),
                    nullable=True)
    op.alter_column('social_media_posts', 'social_platform',
                    existing_type=sa.String(100),
                    nullable=True)


def downgrade() -> None:
    # Revert fields back to required in feedback_submissions table
    op.alter_column('feedback_submissions', 'n8n_execution_id',
                    existing_type=sa.String(255),
                    nullable=False)
    op.alter_column('feedback_submissions', 'email',
                    existing_type=sa.String(255),
                    nullable=False)
    
    # Revert fields back to required in social_media_posts table
    op.alter_column('social_media_posts', 'content_creator',
                    existing_type=sa.String(255),
                    nullable=False)
    op.alter_column('social_media_posts', 'email',
                    existing_type=sa.String(255),
                    nullable=False)
    op.alter_column('social_media_posts', 'social_platform',
                    existing_type=sa.String(100),
                    nullable=False) 