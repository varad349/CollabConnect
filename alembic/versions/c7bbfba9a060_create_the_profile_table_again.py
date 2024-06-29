"""create the profile table again

Revision ID: c7bbfba9a060
Revises: 
Create Date: 2024-03-25 16:30:03.352732

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import JSON

revision: str = 'c7bbfba9a060'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'profiles',
        sa.Column('profile_id', sa.Integer, primary_key=True, index=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('domain', sa.String, index=True),
        sa.Column('github', sa.String, index=True),
        sa.Column('linkedin', sa.String, index=True),
        sa.Column('skills', sa.String, index=True),
        sa.Column('past_projects', JSON),
    )



def downgrade() -> None:
    op.drop_table('profiles')