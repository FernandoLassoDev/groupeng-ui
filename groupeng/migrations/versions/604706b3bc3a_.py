"""empty message

Revision ID: 604706b3bc3a
Revises: 6c78d4b48e76
Create Date: 2020-03-18 13:11:54.972624

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '604706b3bc3a'
down_revision = '6c78d4b48e76'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('specifications',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('manager_id', sa.Integer(), nullable=True),
    sa.Column('header', sa.String(length=32), nullable=True),
    sa.Column('value', sa.String(length=32), nullable=True),
    sa.ForeignKeyConstraint(['manager_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('parameters')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('parameters',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('content', mysql.VARCHAR(length=4096), nullable=True),
    sa.Column('posted', mysql.DATETIME(), nullable=True),
    sa.Column('commenter_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['commenter_id'], [u'users.id'], name=u'parameters_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset=u'utf8',
    mysql_engine=u'InnoDB'
    )
    op.drop_table('specifications')
    # ### end Alembic commands ###
