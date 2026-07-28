"""merge heads

Revision ID: 0812582b63f5
Revises: dd05c538efec, f0bd01a18a3d
Create Date: 2026-07-28 12:30:05.885482

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import open_webui.internal.db


# revision identifiers, used by Alembic.
revision: str = '0812582b63f5'
down_revision: Union[str, None] = ('dd05c538efec', 'f0bd01a18a3d')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
