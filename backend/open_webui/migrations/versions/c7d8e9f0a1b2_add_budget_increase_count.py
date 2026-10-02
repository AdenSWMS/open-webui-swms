"""add recurring budget tracking to user

Revision ID: c7d8e9f0a1b2
Revises: 6b4e2a9f1c30
Create Date: 2026-10-02 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = 'c7d8e9f0a1b2'
down_revision: str | Sequence[str] | None = '6b4e2a9f1c30'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    user_cols = {column['name'] for column in inspector.get_columns('user')}

    if 'budget_increase_count' not in user_cols:
        op.add_column(
            'user',
            sa.Column('budget_increase_count', sa.Integer(), server_default='0', nullable=False),
        )
    if 'budget_base' not in user_cols:
        op.add_column('user', sa.Column('budget_base', sa.Float(), nullable=True))
    if 'budget_period_reset_at' not in user_cols:
        op.add_column('user', sa.Column('budget_period_reset_at', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('user', 'budget_period_reset_at')
    op.drop_column('user', 'budget_base')
    op.drop_column('user', 'budget_increase_count')
