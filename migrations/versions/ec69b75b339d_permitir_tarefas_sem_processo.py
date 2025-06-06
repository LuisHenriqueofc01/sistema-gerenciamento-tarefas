"""Permitir tarefas sem processo

Revision ID: ec69b75b339d
Revises: 12a56d2bfaa0
Create Date: 2025-05-25 15:40:10.330867

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ec69b75b339d'
down_revision = '12a56d2bfaa0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tasks', schema=None) as batch_op:
        batch_op.alter_column('process_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tasks', schema=None) as batch_op:
        batch_op.alter_column('process_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    # ### end Alembic commands ###
