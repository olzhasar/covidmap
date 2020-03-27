"""Location - added api fields

Revision ID: 34bd3ac879b2
Revises: e5d433e6f108
Create Date: 2020-03-28 00:12:21.084937

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '34bd3ac879b2'
down_revision = 'e5d433e6f108'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('location', sa.Column('api_id', sa.Integer(), nullable=True))
    op.add_column('location', sa.Column('api_name', sa.String(length=255), nullable=True))
    op.create_index(op.f('ix_location_api_id'), 'location', ['api_id'], unique=True)
    op.create_index(op.f('ix_location_api_name'), 'location', ['api_name'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_location_api_name'), table_name='location')
    op.drop_index(op.f('ix_location_api_id'), table_name='location')
    op.drop_column('location', 'api_name')
    op.drop_column('location', 'api_id')
    # ### end Alembic commands ###