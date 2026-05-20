"""add_project_member_table

Revision ID: d8f1a2b3c4d5
Revises: b8c9d0e1f2a3
Create Date: 2026-05-20 03:45:25.123939

"""

import uuid
import time
import json
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd8f1a2b3c4d5'
down_revision: Union[str, None] = 'b8c9d0e1f2a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create new table
    op.create_table(
        'project_member',
        sa.Column('id', sa.Text(), primary_key=True, unique=True, nullable=False),
        sa.Column(
            'project_id',
            sa.Text(),
            sa.ForeignKey('project.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column(
            'user_id',
            sa.Text(),
            sa.ForeignKey('user.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column('created_at', sa.BigInteger(), nullable=True),
        sa.Column('updated_at', sa.BigInteger(), nullable=True),
        sa.UniqueConstraint('project_id', 'user_id', name='uq_project_member_project_user'),
    )

    connection = op.get_bind()

    inspector = sa.inspect(connection)
    has_project_table = 'project' in inspector.get_table_names()
    has_user_ids = False
    if has_project_table:
        has_user_ids = 'user_ids' in {col['name'] for col in inspector.get_columns('project')}

    if has_user_ids:
        # 2. Read existing project with user_ids JSON column
        project_table = sa.Table(
            'project',
            sa.MetaData(),
            sa.Column('id', sa.Text()),
            sa.Column('user_ids', sa.JSON()),  # JSON stored as text in SQLite + PG
        )

        results = connection.execute(sa.select(project_table.c.id, project_table.c.user_ids)).fetchall()

        print(results)

        # 3. Insert members into project_member table
        pm_table = sa.Table(
            'project_member',
            sa.MetaData(),
            sa.Column('id', sa.Text()),
            sa.Column('project_id', sa.Text()),
            sa.Column('user_id', sa.Text()),
            sa.Column('created_at', sa.BigInteger()),
            sa.Column('updated_at', sa.BigInteger()),
        )

        now = int(time.time())
        for project_id, user_ids in results:
            if not user_ids:
                continue

            if isinstance(user_ids, str):
                try:
                    user_ids = json.loads(user_ids)
                except Exception:
                    continue  # skip invalid JSON

            if not isinstance(user_ids, list):
                continue

            rows = [
                {
                    'id': str(uuid.uuid4()),
                    'project_id': project_id,
                    'user_id': uid,
                    'created_at': now,
                    'updated_at': now,
                }
                for uid in user_ids
            ]

            if rows:
                connection.execute(pm_table.insert(), rows)

        # 4. Optionally drop the old column
        with op.batch_alter_table('project') as batch:
            batch.drop_column('user_ids')


def downgrade():
    # Reverse: restore user_ids column
    with op.batch_alter_table('project') as batch:
        batch.add_column(sa.Column('user_ids', sa.JSON()))

    connection = op.get_bind()
    pm_table = sa.Table(
        'project_member',
        sa.MetaData(),
        sa.Column('project_id', sa.Text()),
        sa.Column('user_id', sa.Text()),
        sa.Column('created_at', sa.BigInteger()),
        sa.Column('updated_at', sa.BigInteger()),
    )

    project_table = sa.Table(
        'project',
        sa.MetaData(),
        sa.Column('id', sa.Text()),
        sa.Column('user_ids', sa.JSON()),
    )

    # Build JSON arrays again
    results = connection.execute(sa.select(project_table.c.id)).fetchall()

    for (project_id,) in results:
        members = connection.execute(
            sa.select(pm_table.c.user_id).where(pm_table.c.project_id == project_id)
        ).fetchall()

        member_ids = [m[0] for m in members]

        connection.execute(
            project_table.update().where(project_table.c.id == project_id).values(user_ids=member_ids)
        )

    # Drop the new table
    op.drop_table('project_member')
