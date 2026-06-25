# 下载站权限检查
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.models import User
from app.modules.downloads.models import Folder, FolderPermission


async def check_folder_access(
    folder_id: int,
    user: User | None,
    action: str,
    db: AsyncSession,
) -> bool:
    """
    检查当前用户对文件夹是否有指定权限。

    action: "read" | "download" | "upload" | "delete"
    返回: True 表示有权限

    规则:
      - admin 永远有全部权限
      - 当前角色无显式权限记录 → 默认公开（可见文件夹可读可下载，不可上传/删除）
      - 当前角色有显式权限记录 → 按记录判断
    """
    role = user.role if user else "guest"
    if role == "admin":
        return True

    folder = await db.get(Folder, folder_id)
    if folder is None:
        return False

    # 只查询当前角色的权限记录，避免其他角色记录（如 seed 创建的 admin 记录）影响判断
    perms_result = await db.execute(
        select(FolderPermission).where(
            FolderPermission.folder_id == folder_id,
            FolderPermission.role == role,
        )
    )
    role_perm = perms_result.scalar_one_or_none()

    # 当前角色无显式权限记录 → 默认公开（可见文件夹 read/download 开放，upload/delete 关闭）
    if role_perm is None:
        if not folder.is_visible:
            return False
        return action in ("read", "download")

    # 有显式权限记录，按记录判断
    if action == "read":
        return role_perm.can_read
    if action == "download":
        return role_perm.can_download
    return getattr(role_perm, f"can_{action}", False)
