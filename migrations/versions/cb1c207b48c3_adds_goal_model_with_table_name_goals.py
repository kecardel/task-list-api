"""Adds goal model with table name 'goals'

Revision ID: cb1c207b48c3
Revises: 26ed51c311ee
Create Date: 2021-05-11 10:19:48.413877

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cb1c207b48c3'
down_revision = '26ed51c311ee'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('goals',
    sa.Column('goal_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('goal_id')
    )
    op.drop_table('goal')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('goal',
    sa.Column('goal_id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.PrimaryKeyConstraint('goal_id', name='goal_pkey')
    )
    op.drop_table('goals')
    # ### end Alembic commands ###
