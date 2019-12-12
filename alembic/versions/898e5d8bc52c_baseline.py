"""baseline

Revision ID: 898e5d8bc52c
Revises: 
Create Date: 2019-12-12 01:13:05.392839

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '898e5d8bc52c'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'user',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String()),
        sa.Column('win_count', sa.Integer),
        sa.Column('loss_count', sa.Integer),
        sa.Column('dnf_count', sa.Integer),
        sa.Column('idiot_alex_count', sa.Integer))

def downgrade():
    op.drop_table('user')
