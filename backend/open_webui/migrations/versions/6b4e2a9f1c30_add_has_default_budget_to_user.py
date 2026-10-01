"""add has_default_budget to user

Revision ID: 6b4e2a9f1c30
Revises: 2b3c4d5e6f70
Create Date: 2026-10-01 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = '6b4e2a9f1c30'
down_revision: str | None = '2b3c4d5e6f70'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    user_cols = {column['name'] for column in inspector.get_columns('user')}

    if 'has_default_budget' not in user_cols:
        op.add_column(
            'user',
            sa.Column('has_default_budget', sa.Boolean(), server_default=sa.false(), nullable=False),
        )


def downgrade() -> None:
    op.drop_column('user', 'has_default_budget')
