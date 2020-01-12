"""empty message

Revision ID: 0974e891e9ce
Revises: 026acef95f66
Create Date: 2020-01-12 02:42:28.553081

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0974e891e9ce'
down_revision = '026acef95f66'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('notifications',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('idUser', sa.Integer(), nullable=False),
                    sa.Column('message', sa.String(length=255), nullable=False),
                    sa.ForeignKeyConstraint(['idUser'], ['users.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id')
                    )


def downgrade():
    op.drop_table('notifications')
