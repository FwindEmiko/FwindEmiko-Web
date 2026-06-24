"""add upload and delete permissions to folder_permissions

Revision ID: a1b2c3d4e5f6
Revises: 0f7d5aced9ef
Create Date: 2026-06-25 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '0f7d5aced9ef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """为 folder_permissions 表新增 can_upload / can_delete 字段。"""
    op.add_column('folder_permissions', sa.Column('can_upload', sa.Boolean(), nullable=False, server_default=sa.text('0')))
    op.add_column('folder_permissions', sa.Column('can_delete', sa.Boolean(), nullable=False, server_default=sa.text('0')))


def downgrade() -> None:
    """移除 can_upload / can_delete 字段。"""
    op.drop_column('folder_permissions', 'can_delete')
    op.drop_column('folder_permissions', 'can_upload')
