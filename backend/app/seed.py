# 数据库种子数据初始化
# 首次启动时检测 users 表为空则创建默认管理员
import logging

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.modules.auth.models import User
from app.modules.downloads.models import Folder, FolderPermission

logger = logging.getLogger(__name__)

# 默认管理员凭据（首次启动时创建，请登录后立即修改密码）
DEFAULT_ADMIN_USERNAME = "FwindEmi"
DEFAULT_ADMIN_EMAIL = "admin@windemiko.top"
DEFAULT_ADMIN_PASSWORD = "L5201314x"


async def init_seed_data(db: AsyncSession) -> None:
    """检测 users 表是否为空，为空则创建默认管理员"""
    user_count = (
        await db.execute(select(func.count(User.id)))
    ).scalar() or 0

    if user_count > 0:
        logger.info("[seed] users 表已有 %d 条记录，跳过种子数据初始化", user_count)
        return

    logger.warning("[seed] users 表为空，正在创建默认管理员 (admin/admin123)...")
    admin = User(
        username=DEFAULT_ADMIN_USERNAME,
        email=DEFAULT_ADMIN_EMAIL,
        password_hash=hash_password(DEFAULT_ADMIN_PASSWORD),
        display_name="Administrator",
        role="admin",
        is_active=True,
        is_verified=True,
    )
    db.add(admin)
    await db.commit()
    logger.warning(
        "[seed] 默认管理员已创建: username=%s, password=%s (请立即修改密码！)",
        DEFAULT_ADMIN_USERNAME,
        DEFAULT_ADMIN_PASSWORD,
    )


async def ensure_admin_permissions(db: AsyncSession) -> None:
    """为所有现有文件夹补齐 admin 角色的全部权限记录。

    admin 角色在权限检查代码中永远返回 True，但为了权限矩阵 UI 显示完整，
    需要在数据库中存在 admin 的权限记录。
    """
    folders_result = await db.execute(select(Folder.id))
    folder_ids = [row[0] for row in folders_result.all()]
    if not folder_ids:
        return

    for folder_id in folder_ids:
        # 检查是否已存在 admin 权限记录
        existing = await db.execute(
            select(FolderPermission).where(
                FolderPermission.folder_id == folder_id,
                FolderPermission.role == "admin",
            )
        )
        if existing.scalar_one_or_none() is not None:
            continue

        db.add(
            FolderPermission(
                folder_id=folder_id,
                role="admin",
                can_read=True,
                can_download=True,
                can_upload=True,
                can_delete=True,
            )
        )

    await db.commit()
    logger.info("[seed] 已为 %d 个文件夹补齐 admin 权限记录", len(folder_ids))
