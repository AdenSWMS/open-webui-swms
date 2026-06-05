"""Add project table

Revision ID: b8c9d0e1f2a3
Revises: 4ace53fd72c8
Create Date: 2024-11-14 03:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

revision = 'b8c9d0e1f2a3'
down_revision = '4ace53fd72c8'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'project',
        sa.Column('id', sa.Text(), nullable=False, primary_key=True, unique=True),
        sa.Column('user_id', sa.Text(), nullable=True),
        sa.Column('name', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('data', sa.JSON(), nullable=True),
        sa.Column('meta', sa.JSON(), nullable=True),
        sa.Column('permissions', sa.JSON(), nullable=True),
        sa.Column('allowed_model_ids', sa.JSON(), nullable=True),
        sa.Column('user_ids', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.BigInteger(), nullable=True),
        sa.Column('updated_at', sa.BigInteger(), nullable=True),
    )



def downgrade():
    op.drop_table('project')
