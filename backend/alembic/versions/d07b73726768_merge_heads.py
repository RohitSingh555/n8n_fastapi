"""merge heads

Revision ID: d07b73726768
Revises: 002_add_separate_image_llm_fields, 59efc466aed4
Create Date: 2025-08-13 20:28:40.378801

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd07b73726768'
down_revision = ('002_add_separate_image_llm_fields', '59efc466aed4')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass 