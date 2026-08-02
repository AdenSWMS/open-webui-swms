"""add_project_id to messages for analytics

Revision ID: 383ecd025e64
Revises: 783c9aafa7f8
Create Date: 2026-08-03 00:23:38.362476

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '383ecd025e64'
down_revision: Union[str, None] = '783c9aafa7f8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Füge nur die project_id Spalte zu chat_message hinzu
    op.add_column('chat_message', sa.Column('project_id', sa.Text(), nullable=True))
    op.create_index(op.f('ix_chat_message_project_id'), 'chat_message', ['project_id'], unique=False)


def downgrade() -> None:
    # Macht die Änderung sauber rückgängig
    op.drop_index(op.f('ix_chat_message_project_id'), table_name='chat_message')
    op.drop_column('chat_message', 'project_id')