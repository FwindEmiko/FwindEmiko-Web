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

    action: "read" | "download"
    返回: True 表示有权限

    规则:
      - admin 永远有全部权限
      - 文件夹没有任何 FolderPermission 记录 → 公开（所有角色可读可下载）
      - 否则按角色和显式权限规则判断
    """
    role = user.role if user else "guest"
    if role == "admin":
        return True

    folder = await db.get(Folder, folder_id)
    if folder is None:
        return False

    perms_result = await db.execute(
        select(FolderPermission).where(FolderPermission.folder_id == folder_id)
    )
    perms = list(perms_result.scalars().all())

    # 无权限记录 → 默认公开
    if not perms:
        return True

    role_perm = next((p for p in perms if p.role == role), None)

    if role == "author":
        # author 默认可查看所有可见文件夹
        if action == "read":
            return folder.is_visible
        # 下载需显式授权，否则默认可下载可见文件夹
        if role_perm:
            return role_perm.can_download
        return folder.is_visible

    if role == "member":
        if not folder.is_visible:
            return False
        if role_perm:
            return role_perm.can_read if action == "read" else role_perm.can_download
        # 可见但无显式权限时默认可读、不可下载
        return action == "read"

    # guest
    if not folder.is_visible:
        return False
    if role_perm:
        return role_perm.can_read if action == "read" else role_perm.can_download
    return False
