"""add explicit project sharing flag to chats

Revision ID: 2b3c4d5e6f70
Revises: 1a2b3c4d5e6f
Create Date: 2026-09-23

"""
from alembic import op
import sqlalchemy as sa


revision = '2b3c4d5e6f70'
down_revision = '1a2b3c4d5e6f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('chat', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('shared_with_project', sa.Boolean(), nullable=False, server_default=sa.false())
        )
        batch_op.create_index(
            batch_op.f('ix_chat_shared_with_project'),
            ['shared_with_project'],
            unique=False,
        )


def downgrade() -> None:
    with op.batch_alter_table('chat', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_chat_shared_with_project'))
        batch_op.drop_column('shared_with_project')
