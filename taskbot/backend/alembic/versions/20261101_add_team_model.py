"""add_team_model

Revision ID: add_team_model
Revises: 8e3a28c04bca
Create Date: 2026-11-01 12:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_team_model'
down_revision: Union[str, None] = '8e3a28c04bca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create teams table
    op.create_table(
        'teams',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Add team_id column to users table
    op.add_column('users', sa.Column('team_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_users_team', 'users', 'teams', ['team_id'], ['id'])


def downgrade() -> None:
    # Remove team_id from users
    op.drop_constraint('fk_users_team', 'users', type_='foreignkey')
    op.drop_column('users', 'team_id')
    
    # Drop teams table
    op.drop_table('teams')
