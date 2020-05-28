"""empty message

Revision ID: 049f324735da
Revises: b307244ae754
Create Date: 2020-05-03 18:21:20.062918

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '049f324735da'
down_revision = 'b307244ae754'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('class_csv',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('studentID', sa.String(length=32), nullable=True),
    sa.Column('key', sa.String(length=32), nullable=True),
    sa.Column('value', sa.String(length=32), nullable=True),
    sa.Column('manager_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['manager_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('class')
    op.drop_table('student_properties')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('student_properties',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('manager_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('x1', mysql.VARCHAR(length=32), nullable=True),
    sa.Column('x2', mysql.VARCHAR(length=32), nullable=True),
    sa.Column('x3', mysql.VARCHAR(length=32), nullable=True),
    sa.Column('x4', mysql.VARCHAR(length=32), nullable=True),
    sa.Column('x5', mysql.VARCHAR(length=32), nullable=True),
    sa.Column('x6', mysql.VARCHAR(length=32), nullable=True),
    sa.Column('x7', mysql.VARCHAR(length=32), nullable=True),
    sa.Column('x8', mysql.VARCHAR(length=32), nullable=True),
    sa.Column('x9', mysql.VARCHAR(length=32), nullable=True),
    sa.Column('x10', mysql.VARCHAR(length=32), nullable=True),
    sa.Column('number', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['manager_id'], [u'users.id'], name=u'student_properties_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset=u'utf8',
    mysql_engine=u'InnoDB'
    )
    op.create_table('class',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('x1', mysql.VARCHAR(length=32), nullable=True),
    sa.Column('x2', mysql.VARCHAR(length=32), nullable=True),
    sa.Column('x3', mysql.VARCHAR(length=32), nullable=True),
    sa.Column('x4', mysql.VARCHAR(length=32), nullable=True),
    sa.Column('x5', mysql.VARCHAR(length=32), nullable=True),
    sa.Column('x6', mysql.VARCHAR(length=32), nullable=True),
    sa.Column('x7', mysql.VARCHAR(length=32), nullable=True),
    sa.Column('x8', mysql.VARCHAR(length=32), nullable=True),
    sa.Column('x9', mysql.VARCHAR(length=32), nullable=True),
    sa.Column('x10', mysql.VARCHAR(length=32), nullable=True),
    sa.Column('manager_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['manager_id'], [u'users.id'], name=u'class_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset=u'utf8',
    mysql_engine=u'InnoDB'
    )
    op.drop_table('class_csv')
    # ### end Alembic commands ###