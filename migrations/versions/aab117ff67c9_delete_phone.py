"""delete phone

Revision ID: aab117ff67c9
Revises: 804e4ad2f8d1
Create Date: 2022-08-22 10:48:00.048462

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'aab117ff67c9'
down_revision = '804e4ad2f8d1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('phone', table_name='user')
    op.drop_column('user', 'phone')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('phone', mysql.VARCHAR(length=11), nullable=True))
    op.create_index('phone', 'user', ['phone'], unique=True)
    # ### end Alembic commands ###
