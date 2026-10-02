"""add budget baseline fields to user

Revision ID: d7e8f9a0b1c2
Revises: c7d8e9f0a1b2
Create Date: 2026-10-02 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = 'd7e8f9a0b1c2'
down_revision: str | Sequence[str] | None = 'c7d8e9f0a1b2'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    conn = op.get_bind()
    user_cols = {column['name'] for column in sa.inspect(conn).get_columns('user')}

    if 'budget_base' not in user_cols:
        op.add_column('user', sa.Column('budget_base', sa.Float(), nullable=True))
    if 'budget_period_reset_at' not in user_cols:
        op.add_column('user', sa.Column('budget_period_reset_at', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('user', 'budget_period_reset_at')
    op.drop_column('user', 'budget_base')
