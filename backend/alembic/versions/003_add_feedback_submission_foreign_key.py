"""Add feedback_submission_id foreign key to social_media_posts

Revision ID: 003_add_feedback_submission_foreign_key
Revises: d07b73726768
Create Date: 2025-01-14 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003_add_feedback_submission_foreign_key'
down_revision = 'd07b73726768'
branch_labels = None
depends_on = None


def upgrade():
    # Add feedback_submission_id column to social_media_posts table
    op.add_column('social_media_posts', sa.Column('feedback_submission_id', sa.String(255), nullable=True))
    
    # Create index on the new foreign key column
    op.create_index(op.f('ix_social_media_posts_feedback_submission_id'), 'social_media_posts', ['feedback_submission_id'], unique=False)
    
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_social_media_posts_feedback_submission_id',
        'social_media_posts', 'feedback_submissions',
        ['feedback_submission_id'], ['submission_id']
    )


def downgrade():
    # Remove foreign key constraint
    op.drop_constraint('fk_social_media_posts_feedback_submission_id', 'social_media_posts', type_='foreignkey')
    
    # Remove index
    op.drop_index(op.f('ix_social_media_posts_feedback_submission_id'), table_name='social_media_posts')
    
    # Remove column
    op.drop_column('social_media_posts', 'feedback_submission_id')

