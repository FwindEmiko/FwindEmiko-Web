# 角色权限矩阵请求/响应模型
from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field

from app.modules.auth.models import ROLE_PERMISSION_FIELDS


class RolePermissionOut(BaseModel):
    """单个角色的权限配置（用于管理后台展示与编辑）"""

    model_config = ConfigDict(from_attributes=True)

    role: str
    # 文章
    can_create_post: bool = False
    can_edit_own_post: bool = False
    can_delete_own_post: bool = False
    can_publish_post: bool = False
    can_edit_others_post: bool = False
    can_delete_others_post: bool = False
    # 资源
    can_create_resource: bool = False
    can_edit_own_resource: bool = False
    can_delete_own_resource: bool = False
    can_publish_resource: bool = False
    can_edit_others_resource: bool = False
    can_delete_others_resource: bool = False
    # 下载/文件
    can_upload_file: bool = False
    can_download_file: bool = False
    can_delete_file: bool = False
    can_manage_folders: bool = False
    # 分类/标签
    can_manage_categories: bool = False
    can_manage_tags: bool = False
    # 用户管理
    can_view_users: bool = False
    can_manage_users: bool = False
    # AI 对话
    can_use_chat: bool = True
    chat_daily_limit: int = 20
    # 管理员
    can_access_admin: bool = False

    created_at: datetime | None = None
    updated_at: datetime | None = None


class RolePermissionUpdateItem(BaseModel):
    """批量保存时的单条更新项。

    role 用于定位行，其余字段为可更新的权限列。
    admin 角色会被后端强制覆盖为全部 True，前端可只读展示。
    """

    role: str
    can_create_post: bool = False
    can_edit_own_post: bool = False
    can_delete_own_post: bool = False
    can_publish_post: bool = False
    can_edit_others_post: bool = False
    can_delete_others_post: bool = False
    can_create_resource: bool = False
    can_edit_own_resource: bool = False
    can_delete_own_resource: bool = False
    can_publish_resource: bool = False
    can_edit_others_resource: bool = False
    can_delete_others_resource: bool = False
    can_upload_file: bool = False
    can_download_file: bool = False
    can_delete_file: bool = False
    can_manage_folders: bool = False
    can_manage_categories: bool = False
    can_manage_tags: bool = False
    can_view_users: bool = False
    can_manage_users: bool = False
    can_use_chat: bool = True
    chat_daily_limit: int = Field(default=20, ge=0, le=100000)
    can_access_admin: bool = False


class RolePermissionBatchUpdate(BaseModel):
    """批量保存角色权限矩阵"""

    items: List[RolePermissionUpdateItem]


class RolePermissionCreate(BaseModel):
    """新建角色（自定义角色名）"""

    role: str = Field(..., min_length=2, max_length=50, pattern=r"^[a-z0-9_]+$")
    # 新建角色时可携带初始权限，未携带的字段使用数据库默认值
    can_create_post: bool = False
    can_edit_own_post: bool = False
    can_delete_own_post: bool = False
    can_publish_post: bool = False
    can_edit_others_post: bool = False
    can_delete_others_post: bool = False
    can_create_resource: bool = False
    can_edit_own_resource: bool = False
    can_delete_own_resource: bool = False
    can_publish_resource: bool = False
    can_edit_others_resource: bool = False
    can_delete_others_resource: bool = False
    can_upload_file: bool = False
    can_download_file: bool = False
    can_delete_file: bool = False
    can_manage_folders: bool = False
    can_manage_categories: bool = False
    can_manage_tags: bool = False
    can_view_users: bool = False
    can_manage_users: bool = False
    can_use_chat: bool = True
    chat_daily_limit: int = Field(default=20, ge=0, le=100000)
    can_access_admin: bool = False
