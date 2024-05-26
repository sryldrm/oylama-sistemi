"""Add end_time column to Poll model

Revision ID: e1a7be4658a7
Revises: 3b5490e9f17e
Create Date: 2024-05-25 18:23:36.990446

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e1a7be4658a7'
down_revision = '3b5490e9f17e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('poll', schema=None) as batch_op:
        batch_op.add_column(sa.Column('end_time', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('poll', schema=None) as batch_op:
        batch_op.drop_column('end_time')

    # ### end Alembic commands ###