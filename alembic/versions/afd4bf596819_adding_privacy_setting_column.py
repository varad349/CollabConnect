"""adding privacy setting column

Revision ID: afd4bf596819
Revises: f1e527ffc30a
Create Date: 2024-03-26 20:27:12.083724

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'afd4bf596819'
down_revision: Union[str, None] = 'f1e527ffc30a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('profiles', sa.Column('is_private', sa.Boolean(), nullable=False, server_default='false'))



def downgrade() -> None:
    op.drop_column('profiles', 'is_private')