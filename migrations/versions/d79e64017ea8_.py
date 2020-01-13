"""empty message

Revision ID: d79e64017ea8
Revises: 492c5deabff2
Create Date: 2020-01-13 21:27:11.203402

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd79e64017ea8'
down_revision = '492c5deabff2'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('notifications', sa.Column('msgType', sa.INTEGER(), nullable=False))
    op.add_column('notifications', sa.Column('msgDate', sa.DATE(), nullable=False))


def downgrade():
    op.drop_column('notifications', 'msgType')
    op.drop_column('notifications', 'msgDate')
