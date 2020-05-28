"""empty message

Revision ID: b307244ae754
Revises: aec1ccfdbbab
Create Date: 2020-03-21 15:42:27.740927

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'b307244ae754'
down_revision = 'aec1ccfdbbab'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('groups', 'studentID',
               existing_type=mysql.INTEGER(display_width=11),
               type_=sa.String(length=32),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('groups', 'studentID',
               existing_type=sa.String(length=32),
               type_=mysql.INTEGER(display_width=11),
               existing_nullable=True)
    # ### end Alembic commands ###
