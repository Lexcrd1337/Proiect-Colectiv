"""empty message

Revision ID: 492c5deabff2
Revises: 0974e891e9ce
Create Date: 2020-01-13 07:34:27.430000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '492c5deabff2'
down_revision = '0974e891e9ce'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('notifications', 'idUser',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('notifications', 'idUser',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.create_table('message',
    sa.Column('id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('msg', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('iduser', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('idparkingspot', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('actiondate', sa.DATE(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['idparkingspot'], ['parking_spots.id'], name='message_idparkingspot_fkey'),
    sa.ForeignKeyConstraint(['iduser'], ['users.id'], name='message_iduser_fkey'),
    sa.PrimaryKeyConstraint('id', name='message_pkey')
    )
    # ### end Alembic commands ###
