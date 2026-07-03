"""merge heads

Revision ID: dd05c538efec
Revises: 42e2978c7933, d8f1a2b3c4d5
Create Date: 2026-07-03 19:10:05.884939

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import open_webui.internal.db


# revision identifiers, used by Alembic.
revision: str = 'dd05c538efec'
down_revision: Union[str, None] = ('42e2978c7933', 'd8f1a2b3c4d5')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
