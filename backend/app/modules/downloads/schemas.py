# 下载站模块请求/响应模型
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FolderPermissionRule(BaseModel):
    role: str = Field(..., pattern="^(admin|author|member|guest)$")
    can_read: bool = True
    can_download: bool = False
    can_upload: bool = False
    can_delete: bool = False


class FolderBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    slug: str | None = Field(None, max_length=200)
    parent_id: int | None = None
    description: str | None = Field(None, max_length=5000)
    is_visible: bool = True
    sort_order: int = 0


class FolderCreate(FolderBase):
    permission_rules: list[FolderPermissionRule] | None = None


class FolderUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    slug: str | None = Field(None, max_length=200)
    parent_id: int | None = None
    description: str | None = Field(None, max_length=5000)
    is_visible: bool | None = None
    sort_order: int | None = None
    permission_rules: list[FolderPermissionRule] | None = None


class FolderTreeNode(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    description: str | None
    is_visible: bool
    sort_order: int
    children: list["FolderTreeNode"] = []


class BreadcrumbItem(BaseModel):
    id: int
    name: str


class SubFolderItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str


class FileItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    display_name: str | None
    file_size: int
    mime_type: str | None
    download_count: int
    has_external: bool = False
    created_at: datetime


class FolderFilesResponse(BaseModel):
    folder: dict
    breadcrumbs: list[BreadcrumbItem]
    subfolders: list[SubFolderItem]
    files: list[FileItem]


# === 权限矩阵 ===


class PermissionMatrixItem(BaseModel):
    """单个文件夹 + 单个角色的权限条目"""
    folder_id: int
    folder_name: str
    role: str
    can_read: bool
    can_download: bool
    can_upload: bool
    can_delete: bool


class PermissionMatrixFolder(BaseModel):
    """文件夹在权限矩阵中的展示条目"""
    folder_id: int
    folder_name: str
    permissions: list[PermissionMatrixItem]


class PermissionMatrixResponse(BaseModel):
    """权限矩阵响应：所有文件夹 × 所有角色"""
    folders: list[PermissionMatrixFolder]
    roles: list[str] = ["admin", "author", "member", "guest"]


class PermissionBatchUpdateItem(BaseModel):
    folder_id: int
    role: str = Field(..., pattern="^(admin|author|member|guest)$")
    can_read: bool = True
    can_download: bool = False
    can_upload: bool = False
    can_delete: bool = False


class PermissionBatchUpdate(BaseModel):
    """批量更新权限请求"""
    items: list[PermissionBatchUpdateItem]
