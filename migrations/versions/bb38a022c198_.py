"""empty message

Revision ID: bb38a022c198
Revises: b774e0e6ed5f
Create Date: 2021-07-08 09:29:20.072892

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bb38a022c198'
down_revision = 'b774e0e6ed5f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('auth',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.Column('url', sa.String(length=255), nullable=True),
    sa.Column('addtime', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name'),
    sa.UniqueConstraint('url')
    )
    op.create_index(op.f('ix_auth_addtime'), 'auth', ['addtime'], unique=False)
    op.create_table('auth',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.Column('auths', sa.String(length=600), nullable=True),
    sa.Column('addtime', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_role_addtime'), 'auth', ['addtime'], unique=False)
    op.create_table('admin',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.Column('pwd', sa.String(length=100), nullable=True),
    sa.Column('is_super', sa.SmallInteger(), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.Column('addtime', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['auth.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_admin_addtime'), 'admin', ['addtime'], unique=False)
    op.create_table('adminlog',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('admin_id', sa.Integer(), nullable=True),
    sa.Column('ip', sa.String(length=100), nullable=True),
    sa.Column('addtime', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['admin_id'], ['admin.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_adminlog_addtime'), 'adminlog', ['addtime'], unique=False)
    op.create_table('oplog',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('admin_id', sa.Integer(), nullable=True),
    sa.Column('ip', sa.String(length=100), nullable=True),
    sa.Column('reason', sa.String(length=600), nullable=True),
    sa.Column('addtime', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['admin_id'], ['admin.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_oplog_addtime'), 'oplog', ['addtime'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_oplog_addtime'), table_name='oplog')
    op.drop_table('oplog')
    op.drop_index(op.f('ix_adminlog_addtime'), table_name='adminlog')
    op.drop_table('adminlog')
    op.drop_index(op.f('ix_admin_addtime'), table_name='admin')
    op.drop_table('admin')
    op.drop_index(op.f('ix_role_addtime'), table_name='auth')
    op.drop_table('auth')
    op.drop_index(op.f('ix_auth_addtime'), table_name='auth')
    op.drop_table('auth')
    # ### end Alembic commands ###
