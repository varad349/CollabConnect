"""Adding projects_list column to User table 

Revision ID: f1e527ffc30a
Revises: c7bbfba9a060
Create Date: 2024-03-25 19:41:00.302460

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'f1e527ffc30a'
down_revision: Union[str, None] = 'c7bbfba9a060'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('projects_list', postgresql.ARRAY(sa.Integer()), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'projects_list')
