"""empty message

Revision ID: 9fa44a48b40c
Revises: 
Create Date: 2020-03-17 15:39:33.649811

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9fa44a48b40c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('parameters',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('content', sa.String(length=4096), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('parameters')
    # ### end Alembic commands ###
