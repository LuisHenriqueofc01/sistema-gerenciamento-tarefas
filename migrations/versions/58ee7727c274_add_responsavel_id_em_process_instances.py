"""add responsavel_id em process_instances

Revision ID: 58ee7727c274
Revises: 57e7ac953dc9
Create Date: 2025-05-19 20:46:39.730914
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '58ee7727c274'
down_revision = '57e7ac953dc9'
branch_labels = None
depends_on = None


def upgrade():
    # Adiciona a coluna responsavel_id à tabela process_instances
    with op.batch_alter_table('process_instances', schema=None) as batch_op:
        batch_op.add_column(sa.Column('responsavel_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_process_instances_responsavel_id_users',
            'users',
            ['responsavel_id'],
            ['id']
        )

    # Altera campos da tabela users
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column(
            'username',
            existing_type=sa.VARCHAR(length=80),
            type_=sa.String(length=64),
            existing_nullable=False
        )
        batch_op.alter_column(
            'name',
            existing_type=sa.VARCHAR(length=120),
            nullable=True
        )
        batch_op.alter_column(
            'password_hash',
            existing_type=sa.VARCHAR(length=255),
            type_=sa.String(length=128),
            nullable=True
        )


def downgrade():
    # Reverte as alterações na tabela users
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column(
            'password_hash',
            existing_type=sa.String(length=128),
            type_=sa.VARCHAR(length=255),
            nullable=False
        )
        batch_op.alter_column(
            'name',
            existing_type=sa.VARCHAR(length=120),
            nullable=False
        )
        batch_op.alter_column(
            'username',
            existing_type=sa.String(length=64),
            type_=sa.VARCHAR(length=80),
            existing_nullable=False
        )

    # Remove a foreign key e a coluna responsavel_id
    with op.batch_alter_table('process_instances', schema=None) as batch_op:
        batch_op.drop_constraint('fk_process_instances_responsavel_id_users', type_='foreignkey')
        batch_op.drop_column('responsavel_id')
