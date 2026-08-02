"""add_project_to_chats

Revision ID: 783c9aafa7f8
Revises: 0812582b63f5
Create Date: 2026-07-31 13:12:48.949669

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '783c9aafa7f8'
down_revision: Union[str, None] = '0812582b63f5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Spalte 'project_id' zur Chat-Tabelle hinzufügen
    with op.batch_alter_table('chat', schema=None) as batch_op:
        batch_op.add_column(sa.Column('project_id', sa.String(), nullable=True))
        batch_op.create_index(batch_op.f('ix_chat_project_id'), ['project_id'], unique=False)

    # 2. Spalte 'project_id' zur Chat_File-Tabelle hinzufügen
    with op.batch_alter_table('chat_file', schema=None) as batch_op:
        batch_op.add_column(sa.Column('project_id', sa.Text(), nullable=True))


def downgrade() -> None:
    # Rückgängig machen im Batch-Modus
    with op.batch_alter_table('chat_file', schema=None) as batch_op:
        batch_op.drop_column('project_id')

    with op.batch_alter_table('chat', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_chat_project_id'))
        batch_op.drop_column('project_id')