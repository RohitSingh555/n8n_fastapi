"""make_all_fields_optional

Revision ID: 59efc466aed4
Revises: 001_initial_schema
Create Date: 2025-08-13 11:18:55.526260

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite


# revision identifiers, used by Alembic.
revision = '59efc466aed4'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # SQLite doesn't support ALTER COLUMN, so we need to recreate tables
    # This is a SQLite-specific workaround
    
    # Recreate feedback_submissions table with nullable fields
    with op.batch_alter_table('feedback_submissions') as batch_op:
        batch_op.alter_column('n8n_execution_id', nullable=True)
        batch_op.alter_column('email', nullable=True)
    
    # Recreate social_media_posts table with nullable fields
    with op.batch_alter_table('social_media_posts') as batch_op:
        batch_op.alter_column('content_creator', nullable=True)
        batch_op.alter_column('email', nullable=True)
        batch_op.alter_column('social_platform', nullable=True)


def downgrade() -> None:
    # Revert fields back to required using batch operations
    with op.batch_alter_table('feedback_submissions') as batch_op:
        batch_op.alter_column('n8n_execution_id', nullable=False)
        batch_op.alter_column('email', nullable=False)
    
    with op.batch_alter_table('social_media_posts') as batch_op:
        batch_op.alter_column('content_creator', nullable=False)
        batch_op.alter_column('email', nullable=False)
        batch_op.alter_column('social_platform', nullable=False) 