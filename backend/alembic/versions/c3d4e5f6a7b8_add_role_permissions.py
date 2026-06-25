"""add role_permissions table

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-06-25 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, Sequence[str], None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """创建 role_permissions 表（角色细粒度权限矩阵）"""
    op.create_table(
        'role_permissions',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('role', sa.String(length=50), nullable=False, unique=True),
        # 文章
        sa.Column('can_create_post', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('can_edit_own_post', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('can_delete_own_post', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('can_publish_post', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('can_edit_others_post', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('can_delete_others_post', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        # 资源
        sa.Column('can_create_resource', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('can_edit_own_resource', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('can_delete_own_resource', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('can_publish_resource', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('can_edit_others_resource', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('can_delete_others_resource', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        # 下载/文件
        sa.Column('can_upload_file', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('can_download_file', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('can_delete_file', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('can_manage_folders', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        # 分类/标签
        sa.Column('can_manage_categories', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('can_manage_tags', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        # 用户管理
        sa.Column('can_view_users', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('can_manage_users', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        # AI 对话
        sa.Column('can_use_chat', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('chat_daily_limit', sa.Integer(), nullable=False, server_default='20'),
        # 管理员
        sa.Column('can_access_admin', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        # 时间戳
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_role_permissions_role', 'role_permissions', ['role'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_role_permissions_role', table_name='role_permissions')
    op.drop_table('role_permissions')
