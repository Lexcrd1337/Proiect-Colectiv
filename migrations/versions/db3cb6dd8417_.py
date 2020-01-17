"""empty message

Revision ID: db3cb6dd8417
Revises: d79e64017ea8
Create Date: 2020-01-17 17:44:35.466957

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'db3cb6dd8417'
down_revision = 'd79e64017ea8'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('sections_users')
    op.drop_table('user_roles')
    op.drop_table('submissions')
    op.drop_table('sections')
    op.drop_table('qualifiers')
    op.drop_table('conferences_users')
    op.drop_table('roles')
    op.drop_table('papers')
    op.drop_table('conferences')


def downgrade():
    pass
