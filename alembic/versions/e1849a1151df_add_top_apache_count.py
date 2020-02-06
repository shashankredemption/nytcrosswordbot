"""Add Top Apache Count

Revision ID: e1849a1151df
Revises: 36a43ecd70b2
Create Date: 2020-02-06 02:37:45.138173

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e1849a1151df'
down_revision = '36a43ecd70b2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('top_apache_count', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'top_apache_count')
    # ### end Alembic commands ###
