"""Added channel ID to the database

Revision ID: 1a920619b476
Revises: a57289e5ba35
Create Date: 2020-09-18 15:12:37.430849

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1a920619b476'
down_revision = 'a57289e5ba35'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('reactions', sa.Column('channel_id', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('reactions', 'channel_id')
    # ### end Alembic commands ###
