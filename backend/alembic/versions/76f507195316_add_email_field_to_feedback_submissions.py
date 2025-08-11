"""Add email field to feedback submissions

Revision ID: 76f507195316
Revises: 
Create Date: 2025-08-06 13:24:52.798619

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '76f507195316'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add email column to feedback_submissions table
    op.add_column('feedback_submissions', sa.Column('email', sa.String(255), nullable=False))


def downgrade() -> None:
    # Remove email column from feedback_submissions table
    op.drop_column('feedback_submissions', 'email') 