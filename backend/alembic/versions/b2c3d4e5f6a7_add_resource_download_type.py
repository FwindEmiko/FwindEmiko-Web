"""add download_type and external_label to resource_versions

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-06-25 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """为 resource_versions 表新增 download_type / external_label 字段。"""
    # download_type 默认 'local'，兼容旧数据（已有 file_url 的视为本站上传）
    op.add_column(
        'resource_versions',
        sa.Column('download_type', sa.String(length=20), nullable=False, server_default='local'),
    )
    op.add_column(
        'resource_versions',
        sa.Column('external_label', sa.String(length=100), nullable=True),
    )
    # 数据迁移：有 external_url 的旧记录自动标记为 external 类型
    op.execute(
        "UPDATE resource_versions SET download_type='external' WHERE external_url IS NOT NULL AND external_url != ''"
    )


def downgrade() -> None:
    """移除 download_type / external_label 字段。"""
    op.drop_column('resource_versions', 'external_label')
    op.drop_column('resource_versions', 'download_type')
