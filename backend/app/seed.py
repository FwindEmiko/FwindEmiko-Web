# 数据库种子数据初始化
# 首次启动时检测 users 表为空则创建默认管理员
import logging

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.modules.auth.models import User, RolePermission
from app.modules.downloads.models import Folder, FolderPermission

logger = logging.getLogger(__name__)

# 默认管理员凭据（首次启动时创建，请登录后立即修改密码）
DEFAULT_ADMIN_USERNAME = "FwindEmi"
DEFAULT_ADMIN_EMAIL = "admin@windemiko.top"
DEFAULT_ADMIN_PASSWORD = "L5201314x"


# 预置角色权限矩阵
# True = 该角色默认拥有此权限；False = 默认无此权限
# admin 行所有布尔权限强制为 True，chat_daily_limit 不限（设大值）
_PRESET_ROLE_PERMISSIONS: list[dict] = [
    {
        "role": "admin",
        # 全部权限 True（在 ensure_role_permissions 中会强制覆盖为 True，这里仅为可读性）
        "can_create_post": True, "can_edit_own_post": True, "can_delete_own_post": True,
        "can_publish_post": True, "can_edit_others_post": True, "can_delete_others_post": True,
        "can_create_resource": True, "can_edit_own_resource": True, "can_delete_own_resource": True,
        "can_publish_resource": True, "can_edit_others_resource": True, "can_delete_others_resource": True,
        "can_upload_file": True, "can_download_file": True, "can_delete_file": True, "can_manage_folders": True,
        "can_manage_categories": True, "can_manage_tags": True,
        "can_view_users": True, "can_manage_users": True,
        "can_use_chat": True, "chat_daily_limit": 9999,
        "can_access_admin": True,
    },
    {
        "role": "author",
        # 文章/资源 CRUD（只限自己的），可发布，聊天无限
        "can_create_post": True, "can_edit_own_post": True, "can_delete_own_post": True,
        "can_publish_post": True, "can_edit_others_post": False, "can_delete_others_post": False,
        "can_create_resource": True, "can_edit_own_resource": True, "can_delete_own_resource": True,
        "can_publish_resource": True, "can_edit_others_resource": False, "can_delete_others_resource": False,
        "can_upload_file": True, "can_download_file": True, "can_delete_file": False, "can_manage_folders": False,
        "can_manage_categories": False, "can_manage_tags": True,
        "can_view_users": False, "can_manage_users": False,
        "can_use_chat": True, "chat_daily_limit": 9999,
        "can_access_admin": True,
    },
    {
        "role": "moderator",
        # author 权限 + 可编辑他人文章 + 管理分类/标签
        "can_create_post": True, "can_edit_own_post": True, "can_delete_own_post": True,
        "can_publish_post": True, "can_edit_others_post": True, "can_delete_others_post": False,
        "can_create_resource": True, "can_edit_own_resource": True, "can_delete_own_resource": True,
        "can_publish_resource": True, "can_edit_others_resource": True, "can_delete_others_resource": False,
        "can_upload_file": True, "can_download_file": True, "can_delete_file": True, "can_manage_folders": True,
        "can_manage_categories": True, "can_manage_tags": True,
        "can_view_users": True, "can_manage_users": False,
        "can_use_chat": True, "chat_daily_limit": 9999,
        "can_access_admin": True,
    },
    {
        "role": "member",
        # 可下载文件，可聊天（20条/天）
        "can_create_post": False, "can_edit_own_post": False, "can_delete_own_post": False,
        "can_publish_post": False, "can_edit_others_post": False, "can_delete_others_post": False,
        "can_create_resource": False, "can_edit_own_resource": False, "can_delete_own_resource": False,
        "can_publish_resource": False, "can_edit_others_resource": False, "can_delete_others_resource": False,
        "can_upload_file": False, "can_download_file": True, "can_delete_file": False, "can_manage_folders": False,
        "can_manage_categories": False, "can_manage_tags": False,
        "can_view_users": False, "can_manage_users": False,
        "can_use_chat": True, "chat_daily_limit": 20,
        "can_access_admin": False,
    },
    {
        "role": "guest",
        # 仅下载公开文件，聊天 5条/天
        "can_create_post": False, "can_edit_own_post": False, "can_delete_own_post": False,
        "can_publish_post": False, "can_edit_others_post": False, "can_delete_others_post": False,
        "can_create_resource": False, "can_edit_own_resource": False, "can_delete_own_resource": False,
        "can_publish_resource": False, "can_edit_others_resource": False, "can_delete_others_resource": False,
        "can_upload_file": False, "can_download_file": True, "can_delete_file": False, "can_manage_folders": False,
        "can_manage_categories": False, "can_manage_tags": False,
        "can_view_users": False, "can_manage_users": False,
        "can_use_chat": True, "chat_daily_limit": 5,
        "can_access_admin": False,
    },
]


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


async def ensure_role_permissions(db: AsyncSession) -> None:
    """确保 role_permissions 表存在全部预置角色行。

    幂等：已存在的角色行不覆盖（保留管理员通过 UI 的自定义修改），
    缺失的角色行按 _PRESET_ROLE_PERMISSIONS 插入。
    admin 行强制保持全部布尔权限为 True，防止误锁。
    """
    existing_result = await db.execute(select(RolePermission.role))
    existing_roles = {row[0] for row in existing_result.all()}

    for preset in _PRESET_ROLE_PERMISSIONS:
        if preset["role"] in existing_roles:
            # admin 行强制全开（防止之前被误改为 False 导致系统不可用）
            if preset["role"] == "admin":
                rp_result = await db.execute(
                    select(RolePermission).where(RolePermission.role == "admin")
                )
                rp = rp_result.scalar_one_or_none()
                if rp is not None:
                    for field in (
                        "can_create_post", "can_edit_own_post", "can_delete_own_post",
                        "can_publish_post", "can_edit_others_post", "can_delete_others_post",
                        "can_create_resource", "can_edit_own_resource", "can_delete_own_resource",
                        "can_publish_resource", "can_edit_others_resource", "can_delete_others_resource",
                        "can_upload_file", "can_download_file", "can_delete_file", "can_manage_folders",
                        "can_manage_categories", "can_manage_tags",
                        "can_view_users", "can_manage_users",
                        "can_use_chat", "can_access_admin",
                    ):
                        setattr(rp, field, True)
                    rp.chat_daily_limit = 9999
            continue

        # 插入新行
        data = dict(preset)
        db.add(RolePermission(**data))

    await db.commit()
    logger.info(
        "[seed] role_permissions 表已补齐 %d 个预置角色（已有 %d 个）",
        len(_PRESET_ROLE_PERMISSIONS),
        len(existing_roles),
    )
