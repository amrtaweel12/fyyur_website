"""empty message

Revision ID: 6ae826ac8ddd
Revises: 144cf7179caa
Create Date: 2023-08-06 13:40:57.653110

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '6ae826ac8ddd'
down_revision = '144cf7179caa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('show', schema=None) as batch_op:
        batch_op.add_column(sa.Column('show_date', sa.DateTime(), nullable=True))
        batch_op.drop_column('date')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('show', schema=None) as batch_op:
        batch_op.add_column(sa.Column('date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
        batch_op.drop_column('show_date')

    # ### end Alembic commands ###
