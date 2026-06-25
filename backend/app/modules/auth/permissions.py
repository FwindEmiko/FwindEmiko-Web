# 角色细粒度权限依赖
# 提供 FastAPI Depends 用的权限检查器，替代旧的 require_role(*roles)
from functools import lru_cache
from typing import Awaitable, Callable

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.modules.auth.dependencies import get_current_user, get_current_user_optional
from app.modules.auth.models import User, RolePermission, ROLE_PERMISSION_FIELDS


# 保留动作名清单（与 ROLE_PERMISSION_FIELDS 同步，用于配置 UI 分组展示）
PERMISSION_ACTION_FIELDS = ROLE_PERMISSION_FIELDS


# 每次请求都会从 DB 重新读取当前用户角色的权限行。
# 不使用 lru_cache 是因为权限矩阵可能被管理员动态修改，缓存会导致修改不立即生效。
async def load_role_permission(
    role: str,
    db: AsyncSession,
) -> RolePermission | None:
    """从数据库加载指定角色的权限行；不存在返回 None。"""
    result = await db.execute(
        select(RolePermission).where(RolePermission.role == role)
    )
    return result.scalar_one_or_none()


def _resolve_role(user: User | None) -> str:
    """解析用户角色：未登录用户视为 guest。"""
    return user.role if user else "guest"


class Permissions:
    """单次请求内的权限检查器。

    用法（在路由参数中注入）::

        @router.post("/posts")
        async def create_post(
            perms: Permissions = Depends(require_permission("can_create_post")),
            ...
        ):
            # 走到这里说明已经有权限
            ...

    或者在函数体内手动检查::

        @router.put("/posts/{post_id}")
        async def update_post(
            user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
            perms: Permissions = Depends(get_permissions),
        ):
            if not perms.can("can_edit_others_post") and post.author_id != user.id:
                raise HTTPException(403, "只能编辑自己的文章")
    """

    def __init__(self, user: User | None, role_perm: RolePermission | None, db: AsyncSession):
        self.user = user
        self.role = _resolve_role(user)
        self.role_perm = role_perm
        self.db = db

    def can(self, action: str) -> bool:
        """检查当前用户是否拥有指定权限。

        - admin 角色永远返回 True（防止误锁导致系统不可用）
        - 未配置角色行时回退到最保守策略：仅有 can_use_chat / can_download_file 默认 True
        """
        if self.role == "admin":
            return True

        if self.role_perm is None:
            # 未在 role_permissions 表中配置该角色：仅放行基础的对话/下载
            return action in ("can_use_chat", "can_download_file")

        # chat_daily_limit 是整数列，单独处理
        if action == "chat_daily_limit":
            return getattr(self.role_perm, action, 0)

        return bool(getattr(self.role_perm, action, False))

    def require(self, action: str) -> None:
        """检查权限，失败抛 403。"""
        if not self.can(action):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"无权执行此操作：{action}",
            )


async def get_permissions(
    user: User | None = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Permissions:
    """加载当前用户的权限检查器（用于在函数体内手动 can/require）。"""
    role = _resolve_role(user)
    role_perm = await load_role_permission(role, db)
    return Permissions(user, role_perm, db)


async def get_permissions_optional(
    user: User | None = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
) -> Permissions:
    """与 get_permissions 类似，但未登录用户不抛 401 而是按 guest 权限判断。

    用于下载类公开接口：未登录用户也能尝试访问，但无权限则 403。
    """
    role = _resolve_role(user)
    role_perm = await load_role_permission(role, db)
    return Permissions(user, role_perm, db)


def require_permission(action: str) -> Callable[[], Awaitable[Permissions]]:
    """生成 FastAPI 依赖：检查当前用户是否拥有指定权限，失败抛 403。

    要求已登录（未登录会先抛 401）。

    用法::

        @router.post("/posts")
        async def create_post(
            perms: Permissions = Depends(require_permission("can_create_post")),
            ...
        ):
            ...
    """

    async def _dependency(
        user: User | None = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> Permissions:
        role = _resolve_role(user)
        role_perm = await load_role_permission(role, db)
        perms = Permissions(user, role_perm, db)
        perms.require(action)
        return perms

    return _dependency


def require_permission_optional(action: str) -> Callable[[], Awaitable[Permissions]]:
    """与 require_permission 类似，但未登录用户不抛 401 而是按 guest 权限判断。

    通常用于下载类接口：未登录用户也能尝试访问，但若无 can_download_file 权限则 403。
    """

    async def _dependency(
        user: User | None = Depends(get_current_user_optional),
        db: AsyncSession = Depends(get_db),
    ) -> Permissions:
        role = _resolve_role(user)
        role_perm = await load_role_permission(role, db)
        perms = Permissions(user, role_perm, db)
        perms.require(action)
        return perms

    return _dependency

