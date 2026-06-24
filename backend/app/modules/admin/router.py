# 后台管理路由
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.response import success
from app.database import get_db
from app.modules.auth.dependencies import require_role
from app.modules.auth.models import User
from app.modules.auth.schemas import UserInfo
from app.modules.blog.models import Post
from app.modules.downloads.models import FileNode
from app.modules.resources.models import Resource

router = APIRouter()


@router.get("/stats")
async def admin_stats(
    _: User = Depends(require_role("admin", "author")),
    db: AsyncSession = Depends(get_db),
):
    """仪表盘统计数据"""
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
    _: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """用户列表（admin only）"""
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
    _: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """修改用户角色（admin only）"""
    if role not in {"admin", "author", "member"}:
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
    _: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """启用/禁用用户（admin only）"""
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
    user: User = Depends(require_role("admin", "author")),
    db: AsyncSession = Depends(get_db),
):
    """管理端文章列表（含草稿）"""
    stmt = select(Post).options(
        selectinload(Post.author), selectinload(Post.category), selectinload(Post.tags)
    )
    count_stmt = select(func.count(Post.id))

    if user.role != "admin":
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
    user: User = Depends(require_role("admin", "author")),
    db: AsyncSession = Depends(get_db),
):
    """管理端获取单篇文章（含草稿）"""
    result = await db.execute(
        select(Post)
        .options(selectinload(Post.author), selectinload(Post.category), selectinload(Post.tags))
        .where(Post.id == post_id)
    )
    post = result.scalar_one_or_none()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文章不存在")
    if user.role != "admin" and post.author_id != user.id:
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
    _: User = Depends(require_role("admin", "author")),
    db: AsyncSession = Depends(get_db),
):
    """管理端资源列表（含草稿）"""
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
    _: User = Depends(require_role("admin", "author")),
    db: AsyncSession = Depends(get_db),
):
    """管理端获取单个资源（含草稿）"""
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
