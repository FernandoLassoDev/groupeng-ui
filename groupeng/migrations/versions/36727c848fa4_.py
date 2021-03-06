"""empty message

Revision ID: 36727c848fa4
Revises: 049f324735da
Create Date: 2020-05-03 18:28:03.932449

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '36727c848fa4'
down_revision = '049f324735da'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('class',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('studentID', sa.String(length=32), nullable=True),
    sa.Column('key', sa.String(length=32), nullable=True),
    sa.Column('value', sa.String(length=32), nullable=True),
    sa.Column('manager_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['manager_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('class_csv')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('class_csv',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('studentID', mysql.VARCHAR(length=32), nullable=True),
    sa.Column('key', mysql.VARCHAR(length=32), nullable=True),
    sa.Column('value', mysql.VARCHAR(length=32), nullable=True),
    sa.Column('manager_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['manager_id'], [u'users.id'], name=u'class_csv_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset=u'utf8',
    mysql_engine=u'InnoDB'
    )
    op.drop_table('class')
    # ### end Alembic commands ###
