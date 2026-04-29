"""add project tables

Revision ID: 6fa8e1f679b0
Revises: 56359461a091
Create Date: 2026-04-29 16:38:55.085519

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import open_webui.internal.db


# revision identifiers, used by Alembic.
revision: str = '6fa8e1f679b0'
down_revision: Union[str, None] = '56359461a091'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create project table
    op.create_table(
        'project',
        sa.Column('id', sa.Text(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('models', open_webui.internal.db.JSONField(), nullable=True),
        sa.Column('created_at', sa.BigInteger(), nullable=False),
        sa.Column('updated_at', sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id'),
    )

    # Create project_user table for many-to-many relationship
    op.create_table(
        'project_user',
        sa.Column('project_id', sa.Text(), nullable=False),
        sa.Column('user_id', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['project.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('project_id', 'user_id'),
    )

    # Add project_id column to chat table
    with op.batch_alter_table('chat', schema=None) as batch_op:
        batch_op.add_column(sa.Column('project_id', sa.Text(), nullable=True))
        batch_op.create_foreign_key('fk_chat_project_id', 'project', ['project_id'], ['id'], ondelete='SET NULL')


def downgrade() -> None:
    with op.batch_alter_table('chat', schema=None) as batch_op:
        batch_op.drop_constraint('fk_chat_project_id', type_='foreignkey')
        batch_op.drop_column('project_id')

    op.drop_table('project_user')
    op.drop_table('project')
