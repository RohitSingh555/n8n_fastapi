"""Add users table

Revision ID: 005
Revises: 004_add_image_url_fields
Create Date: 2025-01-27 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import hashlib

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004_add_image_url_fields'
branch_labels = None
depends_on = None


def upgrade():
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    
    # Insert default users with hashed passwords
    connection = op.get_bind()
    
    # Hash the default password "Pass@1234"
    default_password = "Pass@1234"
    hashed_password = hashlib.sha256(default_password.encode()).hexdigest()
    
    # Insert the three default users
    users_data = [
        {
            'username': 'bob',
            'name': 'Bob',
            'email': 'bob@example.com',
            'password': hashed_password,
            'is_active': True
        },
        {
            'username': 'leah',
            'name': 'Leah',
            'email': 'leah@example.com',
            'password': hashed_password,
            'is_active': True
        },
        {
            'username': 'matthew',
            'name': 'Matthew',
            'email': 'matthew@example.com',
            'password': hashed_password,
            'is_active': True
        }
    ]
    
    for user_data in users_data:
        connection.execute(
            sa.text("""
                INSERT INTO users (username, name, email, password, is_active)
                VALUES (:username, :name, :email, :password, :is_active)
            """),
            user_data
        )


def downgrade():
    # Drop users table
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_table('users')
