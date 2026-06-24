# 资源展示路由
from datetime import datetime, timezone
from math import ceil
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.response import success
from app.database import get_db
from app.modules.auth.dependencies import require_role
from app.modules.auth.models import User
from app.modules.resources import schemas
from app.modules.resources.models import Resource, ResourceVersion, Screenshot
from app.modules.resources.schemas import dump_json_list, parse_json_list
from app.modules.resources.service import generate_unique_slug, save_screenshot

router = APIRouter()


def _resource_to_list_item(resource: Resource, latest_version: ResourceVersion | None) -> dict[str, Any]:
    data = schemas.ResourceListItem.model_validate(resource).model_dump()
    data["game_versions"] = parse_json_list(resource.game_versions)
    data["loaders"] = parse_json_list(resource.loaders)
    data["latest_version"] = schemas.ResourceVersionOut.model_validate(latest_version).model_dump() if latest_version else None
    return data


def _resource_to_detail(resource: Resource) -> dict[str, Any]:
    data = schemas.ResourceDetail.model_validate(resource).model_dump()
    data["game_versions"] = parse_json_list(resource.game_versions)
    data["loaders"] = parse_json_list(resource.loaders)
    return data


@router.get("/resources")
async def list_resources(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    type: str | None = Query(None),
    version: str | None = Query(None),
    loader: str | None = Query(None),
    q: str | None = Query(None, max_length=100),
    sort: str = Query("newest", pattern="^(downloads|newest)$"),
    db: AsyncSession = Depends(get_db),
):
    """公开资源列表，仅返回已发布资源"""
    stmt = (
        select(Resource)
        .options(selectinload(Resource.versions))
        .where(Resource.status == "published")
    )
    count_stmt = select(func.count(Resource.id)).where(Resource.status == "published")

    if type:
        stmt = stmt.where(Resource.type == type)
        count_stmt = count_stmt.where(Resource.type == type)
    if version:
        stmt = stmt.where(Resource.game_versions.ilike(f'%"{version}"%'))
        count_stmt = count_stmt.where(Resource.game_versions.ilike(f'%"{version}"%'))
    if loader:
        stmt = stmt.where(Resource.loaders.ilike(f'%"{loader}"%'))
        count_stmt = count_stmt.where(Resource.loaders.ilike(f'%"{loader}"%'))
    if q:
        stmt = stmt.where(Resource.title.ilike(f"%{q}%"))
        count_stmt = count_stmt.where(Resource.title.ilike(f"%{q}%"))

    total = (await db.execute(count_stmt)).scalar() or 0

    if sort == "downloads":
        stmt = stmt.order_by(Resource.download_count.desc(), Resource.created_at.desc())
    else:
        stmt = stmt.order_by(Resource.created_at.desc())

    stmt = stmt.offset((page - 1) * size).limit(size)
    result = await db.execute(stmt)
    resources = result.scalars().all()

    # 获取每个资源的最新版本
    items = []
    for resource in resources:
        latest = None
        if resource.versions:
            latest = max(resource.versions, key=lambda v: v.created_at)
        items.append(_resource_to_list_item(resource, latest))

    return schemas.PaginatedResources(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=ceil(total / size) if total else 1,
    ).model_dump()


@router.get("/resources/{slug}")
async def get_resource(slug: str, db: AsyncSession = Depends(get_db)):
    """公开资源详情"""
    result = await db.execute(
        select(Resource)
        .options(selectinload(Resource.versions), selectinload(Resource.screenshots))
        .where(Resource.slug == slug, Resource.status == "published")
    )
    resource = result.scalar_one_or_none()
    if resource is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="资源不存在")

    resource.versions = sorted(resource.versions, key=lambda v: v.created_at, reverse=True)
    resource.screenshots = sorted(resource.screenshots, key=lambda s: s.sort_order)
    return success(_resource_to_detail(resource))


@router.post("/resources")
async def create_resource(
    payload: schemas.ResourceCreate,
    user: User = Depends(require_role("admin", "author")),
    db: AsyncSession = Depends(get_db),
):
    """创建资源（author+）"""
    slug = await generate_unique_slug(db, payload.title)
    resource = Resource(
        title=payload.title,
        slug=slug,
        description=payload.description,
        type=payload.type,
        game_versions=dump_json_list(payload.game_versions),
        loaders=dump_json_list(payload.loaders),
        icon_url=payload.icon_url,
        cover_url=payload.cover_url,
    )
    db.add(resource)
    await db.commit()

    result = await db.execute(
        select(Resource)
        .options(selectinload(Resource.versions), selectinload(Resource.screenshots))
        .where(Resource.id == resource.id)
    )
    resource = result.scalar_one()
    return success(_resource_to_detail(resource))


@router.put("/resources/{resource_id}")
async def update_resource(
    resource_id: int,
    payload: schemas.ResourceUpdate,
    user: User = Depends(require_role("admin", "author")),
    db: AsyncSession = Depends(get_db),
):
    """更新资源（author/admin）"""
    result = await db.execute(select(Resource).where(Resource.id == resource_id))
    resource = result.scalar_one_or_none()
    if resource is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="资源不存在")

    if payload.title is not None:
        resource.title = payload.title
        resource.slug = await generate_unique_slug(db, payload.title, exclude_id=resource.id)
    if payload.description is not None:
        resource.description = payload.description
    if payload.type is not None:
        resource.type = payload.type
    if payload.game_versions is not None:
        resource.game_versions = dump_json_list(payload.game_versions)
    if payload.loaders is not None:
        resource.loaders = dump_json_list(payload.loaders)
    if payload.icon_url is not None:
        resource.icon_url = payload.icon_url
    if payload.cover_url is not None:
        resource.cover_url = payload.cover_url
    if payload.status is not None:
        resource.status = payload.status

    resource.updated_at = datetime.now(timezone.utc)
    await db.commit()

    result = await db.execute(
        select(Resource)
        .options(selectinload(Resource.versions), selectinload(Resource.screenshots))
        .where(Resource.id == resource.id)
    )
    resource = result.scalar_one()
    return success(_resource_to_detail(resource))


@router.delete("/resources/{resource_id}")
async def delete_resource(
    resource_id: int,
    user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """删除资源（admin），级联删除版本与截图"""
    result = await db.execute(select(Resource).where(Resource.id == resource_id))
    resource = result.scalar_one_or_none()
    if resource is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="资源不存在")

    await db.delete(resource)
    await db.commit()
    return success(None)


# === 版本 ===


@router.post("/resources/{resource_id}/versions")
async def create_version(
    resource_id: int,
    payload: schemas.ResourceVersionCreate,
    user: User = Depends(require_role("admin", "author")),
    db: AsyncSession = Depends(get_db),
):
    """为资源添加版本（author+）"""
    result = await db.execute(select(Resource).where(Resource.id == resource_id))
    resource = result.scalar_one_or_none()
    if resource is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="资源不存在")

    version = ResourceVersion(
        resource_id=resource_id,
        version_string=payload.version_string,
        changelog=payload.changelog,
        file_url=payload.file_url,
        external_url=payload.external_url,
        file_size=payload.file_size,
        file_hash=payload.file_hash,
        is_prerelease=payload.is_prerelease,
    )
    db.add(version)
    await db.commit()
    await db.refresh(version)
    return success(schemas.ResourceVersionOut.model_validate(version).model_dump())


@router.put("/resources/{resource_id}/versions/{version_id}")
async def update_version(
    resource_id: int,
    version_id: int,
    payload: schemas.ResourceVersionUpdate,
    user: User = Depends(require_role("admin", "author")),
    db: AsyncSession = Depends(get_db),
):
    """更新版本（author/admin）"""
    result = await db.execute(
        select(ResourceVersion).where(
            ResourceVersion.id == version_id, ResourceVersion.resource_id == resource_id
        )
    )
    version = result.scalar_one_or_none()
    if version is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="版本不存在")

    for field in [
        "version_string",
        "changelog",
        "file_url",
        "external_url",
        "file_size",
        "file_hash",
        "is_prerelease",
    ]:
        value = getattr(payload, field)
        if value is not None:
            setattr(version, field, value)

    await db.commit()
    await db.refresh(version)
    return success(schemas.ResourceVersionOut.model_validate(version).model_dump())


@router.delete("/resources/{resource_id}/versions/{version_id}")
async def delete_version(
    resource_id: int,
    version_id: int,
    user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """删除版本（admin）"""
    result = await db.execute(
        select(ResourceVersion).where(
            ResourceVersion.id == version_id, ResourceVersion.resource_id == resource_id
        )
    )
    version = result.scalar_one_or_none()
    if version is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="版本不存在")

    await db.delete(version)
    await db.commit()
    return success(None)


@router.post("/resources/{resource_id}/versions/{version_id}/download")
async def download_version(
    resource_id: int,
    version_id: int,
    db: AsyncSession = Depends(get_db),
):
    """下载计数 + 重定向到实际下载地址"""
    result = await db.execute(
        select(ResourceVersion).where(
            ResourceVersion.id == version_id, ResourceVersion.resource_id == resource_id
        )
    )
    version = result.scalar_one_or_none()
    if version is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="版本不存在")

    version.downloads += 1
    resource_result = await db.execute(select(Resource).where(Resource.id == resource_id))
    resource = resource_result.scalar_one()
    resource.download_count += 1
    resource.updated_at = datetime.now(timezone.utc)
    await db.commit()

    if version.external_url:
        from fastapi.responses import RedirectResponse

        return RedirectResponse(version.external_url)
    if version.file_url:
        from fastapi.responses import RedirectResponse

        return RedirectResponse(version.file_url)

    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="无可用的下载地址")


# === 截图 ===


@router.post("/resources/{resource_id}/screenshots")
async def upload_screenshots(
    resource_id: int,
    files: list[UploadFile] = File(...),
    captions: list[str] = Query(default_factory=list),
    user: User = Depends(require_role("admin", "author")),
    db: AsyncSession = Depends(get_db),
):
    """上传截图（多文件），自动生成缩略图（author+）"""
    result = await db.execute(select(Resource).where(Resource.id == resource_id))
    resource = result.scalar_one_or_none()
    if resource is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="资源不存在")

    max_existing_order = (
        await db.execute(
            select(func.max(Screenshot.sort_order)).where(Screenshot.resource_id == resource_id)
        )
    ).scalar() or -1

    created = []
    for idx, upload in enumerate(files):
        original_url, thumb_url = await save_screenshot(resource_id, upload)
        caption = captions[idx] if idx < len(captions) else None
        screenshot = Screenshot(
            resource_id=resource_id,
            image_url=original_url,
            thumb_url=thumb_url,
            caption=caption,
            sort_order=max_existing_order + 1 + idx,
        )
        db.add(screenshot)
        await db.flush()
        created.append(screenshot)

    await db.commit()
    return success([schemas.ScreenshotOut.model_validate(s).model_dump() for s in created])


@router.put("/resources/{resource_id}/screenshots/reorder")
async def reorder_screenshots(
    resource_id: int,
    payload: schemas.ScreenshotReorder,
    user: User = Depends(require_role("admin", "author")),
    db: AsyncSession = Depends(get_db),
):
    """截图排序（author+）"""
    result = await db.execute(
        select(Screenshot).where(Screenshot.resource_id == resource_id)
    )
    screenshots = {s.id: s for s in result.scalars().all()}

    for order, shot_id in enumerate(payload.screenshot_ids):
        if shot_id in screenshots:
            screenshots[shot_id].sort_order = order

    await db.commit()
    return success(None)


@router.delete("/resources/{resource_id}/screenshots/{shot_id}")
async def delete_screenshot(
    resource_id: int,
    shot_id: int,
    user: User = Depends(require_role("admin", "author")),
    db: AsyncSession = Depends(get_db),
):
    """删除截图（author/admin）"""
    result = await db.execute(
        select(Screenshot).where(
            Screenshot.id == shot_id, Screenshot.resource_id == resource_id
        )
    )
    screenshot = result.scalar_one_or_none()
    if screenshot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="截图不存在")

    await db.delete(screenshot)
    await db.commit()
    return success(None)
