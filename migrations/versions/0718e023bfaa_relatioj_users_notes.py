"""relatioj users-notes

Revision ID: 0718e023bfaa
Revises: 36918efa5775
Create Date: 2024-09-16 16:10:10.504000
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '0718e023bfaa'
down_revision: Union[str, None] = '36918efa5775'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('notes', sa.Column('user_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'notes', 'users', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'notes', type_='foreignkey')
    op.drop_column('notes', 'user_id')
    # ### end Alembic commands ###
