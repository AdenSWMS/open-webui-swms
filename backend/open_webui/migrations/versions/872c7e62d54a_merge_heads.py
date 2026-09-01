"""merge heads

Revision ID: 872c7e62d54a
Revises: 383ecd025e64, d4c1a8e37b62
Create Date: 2026-09-01 10:33:31.096132

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import open_webui.internal.db


# revision identifiers, used by Alembic.
revision: str = '872c7e62d54a'
down_revision: Union[str, None] = ('383ecd025e64', 'd4c1a8e37b62')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
