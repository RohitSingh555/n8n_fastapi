"""add social media posts table

Revision ID: add_social_media_posts_table
Revises: 76f507195316
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_social_media_posts_table'
down_revision = '76f507195316'
branch_labels = None
depends_on = None


def upgrade():
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
    
    # Create indexes
    op.create_index(op.f('ix_social_media_posts_id'), 'social_media_posts', ['id'], unique=False)
    op.create_index(op.f('ix_social_media_posts_post_id'), 'social_media_posts', ['post_id'], unique=True)


def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_social_media_posts_post_id'), table_name='social_media_posts')
    op.drop_index(op.f('ix_social_media_posts_id'), table_name='social_media_posts')
    
    # Drop table
    op.drop_table('social_media_posts')
