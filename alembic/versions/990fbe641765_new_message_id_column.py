"""new message id column

Revision ID: 990fbe641765
Revises:
Create Date: 2018-09-08 00:15:50.387584

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '990fbe641765'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('clocks', sa.Column('message_id', sa.BigInteger, nullable=True))


def downgrade():
    op.drop_column('clocks', 'message_id')
