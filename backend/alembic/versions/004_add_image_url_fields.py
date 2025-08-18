"""Add image_url and uploaded_image_url fields to feedback_submissions

Revision ID: 004_add_image_url_fields
Revises: 003_add_feedback_submission_foreign_key
Create Date: 2025-01-14 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004_add_image_url_fields'
down_revision = '003_add_feedback_submission_foreign_key'
branch_labels = None
depends_on = None


def upgrade():
    # Add image_url and uploaded_image_url columns to feedback_submissions table
    op.add_column('feedback_submissions', sa.Column('image_url', sa.Text(), nullable=True))
    op.add_column('feedback_submissions', sa.Column('uploaded_image_url', sa.Text(), nullable=True))


def downgrade():
    # Remove image_url and uploaded_image_url columns from feedback_submissions table
    op.drop_column('feedback_submissions', 'uploaded_image_url')
    op.drop_column('feedback_submissions', 'image_url')
