# 后台管理路由
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.response import success
from app.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.auth.permissions import (
    Permissions,
    get_permissions,
    require_permission,
)
from app.modules.auth.schemas import UserInfo
from app.modules.blog.models import Post
from app.modules.downloads.models import FileNode
from app.modules.resources.models import Resource

router = APIRouter()


@router.get("/stats")
async def admin_stats(
    _: Permissions = Depends(require_permission("can_access_admin")),
    db: AsyncSession = Depends(get_db),
):
    """仪表盘统计数据（需 can_access_admin）"""
    post_count = (await db.execute(select(func.count(Post.id)))).scalar() or 0
    resource_count = (await db.execute(select(func.count(Resource.id)))).scalar() or 0
    file_count = (await db.execute(select(func.count(FileNode.id)))).scalar() or 0

    resource_downloads = (
        await db.execute(select(func.coalesce(func.sum(Resource.download_count), 0)))
    ).scalar() or 0
    file_downloads = (
        await db.execute(select(func.coalesce(func.sum(FileNode.download_count), 0)))
    ).scalar() or 0

    recent_posts_result = await db.execute(
        select(Post)
        .options(selectinload(Post.author))
        .order_by(desc(Post.created_at))
        .limit(5)
    )
    recent_posts = [
        {
            "id": p.id,
            "title": p.title,
            "status": p.status,
            "author": p.author.username if p.author else None,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }
        for p in recent_posts_result.scalars().all()
    ]

    recent_uploads_result = await db.execute(
        select(FileNode).order_by(desc(FileNode.created_at)).limit(5)
    )
    recent_uploads = [
        {
            "id": f.id,
            "filename": f.filename,
            "folder_id": f.folder_id,
            "created_at": f.created_at.isoformat() if f.created_at else None,
        }
        for f in recent_uploads_result.scalars().all()
    ]

    return success(
        {
            "posts": post_count,
            "resources": resource_count,
            "files": file_count,
            "downloads": int(resource_downloads) + int(file_downloads),
            "recent_posts": recent_posts,
            "recent_uploads": recent_uploads,
        }
    )


@router.get("/users")
async def list_users(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    _: Permissions = Depends(require_permission("can_view_users")),
    db: AsyncSession = Depends(get_db),
):
    """用户列表（需 can_view_users）"""
    total = (await db.execute(select(func.count(User.id)))).scalar() or 0

    result = await db.execute(
        select(User)
        .order_by(desc(User.created_at))
        .offset((page - 1) * size)
        .limit(size)
    )
    users = result.scalars().all()

    return success(
        {
            "items": [UserInfo.model_validate(u).model_dump() for u in users],
            "total": total,
            "page": page,
            "size": size,
        }
    )


@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: int,
    role: str,
    _: Permissions = Depends(require_permission("can_manage_users")),
    db: AsyncSession = Depends(get_db),
):
    """修改用户角色（需 can_manage_users）"""
    if role not in {"admin", "author", "moderator", "member"}:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="无效角色")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    user.role = role
    user.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(user)
    return success(UserInfo.model_validate(user).model_dump())


@router.put("/users/{user_id}/status")
async def update_user_status(
    user_id: int,
    is_active: bool,
    _: Permissions = Depends(require_permission("can_manage_users")),
    db: AsyncSession = Depends(get_db),
):
    """启用/禁用用户（需 can_manage_users）"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    user.is_active = is_active
    user.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(user)
    return success(UserInfo.model_validate(user).model_dump())


@router.get("/posts")
async def admin_list_posts(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),
    category_id: int | None = Query(None),
    q: str | None = Query(None, max_length=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    perms: Permissions = Depends(get_permissions),
):
    """管理端文章列表（需 can_access_admin；非 can_edit_others_post 只能看自己的）"""
    from app.modules.auth.permissions import load_role_permission

    stmt = select(Post).options(
        selectinload(Post.author), selectinload(Post.category), selectinload(Post.tags)
    )
    count_stmt = select(func.count(Post.id))

    # 非管理员且无编辑他人权限，仅能看自己的文章
    if not perms.can("can_edit_others_post"):
        stmt = stmt.where(Post.author_id == user.id)
        count_stmt = count_stmt.where(Post.author_id == user.id)

    if status:
        stmt = stmt.where(Post.status == status)
        count_stmt = count_stmt.where(Post.status == status)
    if category_id:
        stmt = stmt.where(Post.category_id == category_id)
        count_stmt = count_stmt.where(Post.category_id == category_id)
    if q:
        stmt = stmt.where(
            or_(Post.title.ilike(f"%{q}%"), Post.content.ilike(f"%{q}%"))
        )
        count_stmt = count_stmt.where(
            or_(Post.title.ilike(f"%{q}%"), Post.content.ilike(f"%{q}%"))
        )

    total = (await db.execute(count_stmt)).scalar() or 0
    from math import ceil

    stmt = stmt.order_by(Post.created_at.desc()).offset((page - 1) * size).limit(size)
    result = await db.execute(stmt)
    posts = result.scalars().all()

    return success(
        {
            "items": [
                {
                    "id": p.id,
                    "title": p.title,
                    "slug": p.slug,
                    "status": p.status,
                    "is_pinned": p.is_pinned,
                    "category": (
                        {"id": p.category.id, "name": p.category.name, "slug": p.category.slug}
                        if p.category else None
                    ),
                    "tags": [{"id": t.id, "name": t.name, "slug": t.slug} for t in p.tags],
                    "author": (
                        {"id": p.author.id, "username": p.author.username, "display_name": p.author.display_name}
                        if p.author else None
                    ),
                    "created_at": p.created_at.isoformat() if p.created_at else None,
                    "updated_at": p.updated_at.isoformat() if p.updated_at else None,
                }
                for p in posts
            ],
            "total": total,
            "page": page,
            "size": size,
            "pages": ceil(total / size) if total else 1,
        }
    )


@router.get("/posts/{post_id}")
async def admin_get_post(
    post_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    perms: Permissions = Depends(get_permissions),
):
    """管理端获取单篇文章（需 can_access_admin）"""
    result = await db.execute(
        select(Post)
        .options(selectinload(Post.author), selectinload(Post.category), selectinload(Post.tags))
        .where(Post.id == post_id)
    )
    post = result.scalar_one_or_none()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文章不存在")
    # 非作者本人需 can_edit_others_post 权限
    if post.author_id != user.id and not perms.can("can_edit_others_post"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问该文章")

    return success(
        {
            "id": post.id,
            "title": post.title,
            "slug": post.slug,
            "content": post.content,
            "summary": post.summary,
            "cover_url": post.cover_url,
            "status": post.status,
            "is_pinned": post.is_pinned,
            "category_id": post.category_id,
            "tags": [{"id": t.id, "name": t.name, "slug": t.slug} for t in post.tags],
            "author_id": post.author_id,
            "created_at": post.created_at.isoformat() if post.created_at else None,
            "updated_at": post.updated_at.isoformat() if post.updated_at else None,
        }
    )


@router.get("/resources")
async def admin_list_resources(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),
    type: str | None = Query(None),
    q: str | None = Query(None, max_length=100),
    _: Permissions = Depends(require_permission("can_access_admin")),
    db: AsyncSession = Depends(get_db),
):
    """管理端资源列表（需 can_access_admin）"""
    stmt = select(Resource).options(selectinload(Resource.versions))
    count_stmt = select(func.count(Resource.id))

    if status:
        stmt = stmt.where(Resource.status == status)
        count_stmt = count_stmt.where(Resource.status == status)
    if type:
        stmt = stmt.where(Resource.type == type)
        count_stmt = count_stmt.where(Resource.type == type)
    if q:
        stmt = stmt.where(Resource.title.ilike(f"%{q}%"))
        count_stmt = count_stmt.where(Resource.title.ilike(f"%{q}%"))

    total = (await db.execute(count_stmt)).scalar() or 0
    from math import ceil

    stmt = stmt.order_by(Resource.created_at.desc()).offset((page - 1) * size).limit(size)
    result = await db.execute(stmt)
    resources = result.scalars().all()

    items = []
    for r in resources:
        latest = max(r.versions, key=lambda v: v.created_at) if r.versions else None
        items.append(
            {
                "id": r.id,
                "title": r.title,
                "slug": r.slug,
                "type": r.type,
                "status": r.status,
                "download_count": r.download_count,
                "game_versions": __parse_json(r.game_versions),
                "loaders": __parse_json(r.loaders),
                "latest_version": (
                    {
                        "id": latest.id,
                        "resource_id": latest.resource_id,
                        "version_string": latest.version_string,
                        "changelog": latest.changelog,
                        "file_url": latest.file_url,
                        "external_url": latest.external_url,
                        "download_type": latest.download_type,
                        "external_label": latest.external_label,
                        "file_size": latest.file_size,
                        "file_hash": latest.file_hash,
                        "downloads": latest.downloads,
                        "is_prerelease": latest.is_prerelease,
                        "created_at": latest.created_at.isoformat() if latest.created_at else None,
                    }
                    if latest else None
                ),
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "updated_at": r.updated_at.isoformat() if r.updated_at else None,
            }
        )

    return success(
        {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "pages": ceil(total / size) if total else 1,
        }
    )


@router.get("/resources/{resource_id}")
async def admin_get_resource(
    resource_id: int,
    _: Permissions = Depends(require_permission("can_access_admin")),
    db: AsyncSession = Depends(get_db),
):
    """管理端获取单个资源（需 can_access_admin）"""
    result = await db.execute(
        select(Resource)
        .options(selectinload(Resource.versions), selectinload(Resource.screenshots))
        .where(Resource.id == resource_id)
    )
    resource = result.scalar_one_or_none()
    if resource is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="资源不存在")

    versions = sorted(resource.versions, key=lambda v: v.created_at, reverse=True)
    screenshots = sorted(resource.screenshots, key=lambda s: s.sort_order)

    return success(
        {
            "id": resource.id,
            "title": resource.title,
            "slug": resource.slug,
            "description": resource.description,
            "type": resource.type,
            "game_versions": __parse_json(resource.game_versions),
            "loaders": __parse_json(resource.loaders),
            "icon_url": resource.icon_url,
            "cover_url": resource.cover_url,
            "status": resource.status,
            "download_count": resource.download_count,
            "versions": [
                {
                    "id": v.id,
                    "resource_id": v.resource_id,
                    "version_string": v.version_string,
                    "changelog": v.changelog,
                    "file_url": v.file_url,
                    "external_url": v.external_url,
                    "download_type": v.download_type,
                    "external_label": v.external_label,
                    "file_size": v.file_size,
                    "file_hash": v.file_hash,
                    "downloads": v.downloads,
                    "is_prerelease": v.is_prerelease,
                    "created_at": v.created_at.isoformat() if v.created_at else None,
                }
                for v in versions
            ],
            "screenshots": [
                {
                    "id": s.id,
                    "resource_id": s.resource_id,
                    "image_url": s.image_url,
                    "thumb_url": s.thumb_url,
                    "caption": s.caption,
                    "sort_order": s.sort_order,
                }
                for s in screenshots
            ],
            "created_at": resource.created_at.isoformat() if resource.created_at else None,
            "updated_at": resource.updated_at.isoformat() if resource.updated_at else None,
        }
    )


def __parse_json(value: str | list | None) -> list[str]:
    import json

    if not value:
        return []
    if isinstance(value, list):
        return [str(x) for x in value]
    try:
        data = json.loads(value)
        return [str(x) for x in data] if isinstance(data, list) else []
    except Exception:
        return []


# === 角色权限矩阵管理接口（需 can_manage_users） ===

from app.modules.auth.models import RolePermission
from app.modules.auth.role_schemas import (
    RolePermissionBatchUpdate,
    RolePermissionCreate,
    RolePermissionOut,
)


@router.get("/role-permissions")
async def list_role_permissions(
    _: Permissions = Depends(require_permission("can_manage_users")),
    db: AsyncSession = Depends(get_db),
):
    """返回所有角色的权限矩阵（需 can_manage_users）

    admin 角色行强制返回全部权限 True（即使数据库行不存在也会构造默认行）。
    """
    result = await db.execute(select(RolePermission).order_by(RolePermission.id))
    rows = list(result.scalars().all())

    # 确保 admin 行始终存在且全开
    has_admin = any(r.role == "admin" for r in rows)
    if not has_admin:
        admin_row = RolePermission(role="admin")
        # 全部布尔权限强制 True
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
            setattr(admin_row, field, True)
        admin_row.chat_daily_limit = 9999
        rows.insert(0, admin_row)
    else:
        # 已存在 admin 行：强制返回时也保证 True（不修改数据库，仅响应）
        admin_row = next(r for r in rows if r.role == "admin")
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
            # 直接 setattr 到 ORM 实例上，model_validate 时会读到 True
            # 注意：这里不 commit，仅影响响应序列化
            object.__setattr__(admin_row, field, True)

    return success([RolePermissionOut.model_validate(r).model_dump() for r in rows])


@router.put("/role-permissions")
async def update_role_permissions(
    payload: RolePermissionBatchUpdate,
    _: Permissions = Depends(require_permission("can_manage_users")),
    db: AsyncSession = Depends(get_db),
):
    """批量保存角色权限矩阵（需 can_manage_users）

    - 对每个 role 执行 upsert（存在则更新，不存在则插入）
    - admin 角色强制保持全部 True，忽略前端传值
    """
    # 拉取现有全部行
    result = await db.execute(select(RolePermission))
    existing_map: dict[str, RolePermission] = {r.role: r for r in result.scalars().all()}

    for item in payload.items:
        if item.role == "admin":
            # admin 强制全开，不修改
            continue

        if item.role in existing_map:
            rp = existing_map[item.role]
        else:
            # 新角色行
            rp = RolePermission(role=item.role)
            db.add(rp)
            existing_map[item.role] = rp

        # 更新全部权限字段
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
            setattr(rp, field, getattr(item, field))
        rp.chat_daily_limit = item.chat_daily_limit

    await db.commit()
    return success(None)


@router.post("/role-permissions")
async def create_role_permission(
    payload: RolePermissionCreate,
    _: Permissions = Depends(require_permission("can_manage_users")),
    db: AsyncSession = Depends(get_db),
):
    """新建角色（需 can_manage_users）

    - role 名必须为小写字母+数字+下划线
    - 已存在的 role 会返回 422
    - admin 角色不允许通过此接口创建（保留给 seed）
    """
    if payload.role == "admin":
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="admin 角色由系统保留")

    existing = await db.execute(select(RolePermission).where(RolePermission.role == payload.role))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"角色 {payload.role} 已存在")

    rp = RolePermission(role=payload.role)
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
        setattr(rp, field, getattr(payload, field))
    rp.chat_daily_limit = payload.chat_daily_limit

    db.add(rp)
    await db.commit()
    await db.refresh(rp)
    return success(RolePermissionOut.model_validate(rp).model_dump())
