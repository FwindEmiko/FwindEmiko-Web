# 博客路由
from datetime import datetime, timezone
from math import ceil
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, or_, select
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
from app.modules.blog import schemas
from app.modules.blog.models import Category, Post, Tag, post_tags
from app.modules.blog.service import generate_unique_slug, render_md

router = APIRouter()


def _post_to_detail(post: Post) -> dict[str, Any]:
    data = schemas.PostListItem.model_validate(post).model_dump()
    data["content_md"] = post.content
    data["content_html"] = render_md(post.content)
    return data


@router.get("/posts", response_model=schemas.PaginatedPosts)
async def list_posts(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    category: str | None = Query(None),
    tag: str | None = Query(None),
    q: str | None = Query(None, max_length=100),
    db: AsyncSession = Depends(get_db),
):
    """公开文章列表，仅返回已发布文章"""
    stmt = (
        select(Post)
        .options(selectinload(Post.author), selectinload(Post.category), selectinload(Post.tags))
        .where(Post.status == "published")
    )

    if category:
        stmt = stmt.join(Category).where(Category.slug == category)
    if tag:
        stmt = stmt.join(post_tags).join(Tag).where(Tag.slug == tag)
    if q:
        stmt = stmt.where(or_(Post.title.ilike(f"%{q}%"), Post.content.ilike(f"%{q}%")))

    count_stmt = select(func.count(Post.id)).where(Post.status == "published")
    if category:
        count_stmt = count_stmt.join(Category).where(Category.slug == category)
    if tag:
        count_stmt = count_stmt.join(post_tags).join(Tag).where(Tag.slug == tag)
    if q:
        count_stmt = count_stmt.where(or_(Post.title.ilike(f"%{q}%"), Post.content.ilike(f"%{q}%")))

    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = stmt.order_by(Post.is_pinned.desc(), Post.published_at.desc(), Post.id.desc())
    stmt = stmt.offset((page - 1) * size).limit(size)

    result = await db.execute(stmt)
    posts = result.scalars().all()

    return schemas.PaginatedPosts(
        items=[schemas.PostListItem.model_validate(p) for p in posts],
        total=total,
        page=page,
        size=size,
        pages=ceil(total / size) if total else 1,
    ).model_dump()


@router.get("/posts/{slug}")
async def get_post(slug: str, db: AsyncSession = Depends(get_db)):
    """公开文章详情，自动增加浏览量"""
    result = await db.execute(
        select(Post)
        .options(selectinload(Post.author), selectinload(Post.category), selectinload(Post.tags))
        .where(Post.slug == slug, Post.status == "published")
    )
    post = result.scalar_one_or_none()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文章不存在")

    post.view_count += 1
    await db.commit()

    # 提交后重新加载完整关系，避免异步 ORM 懒加载失败
    result = await db.execute(
        select(Post)
        .options(selectinload(Post.author), selectinload(Post.category), selectinload(Post.tags))
        .where(Post.id == post.id)
    )
    post = result.scalar_one()

    # 上一篇 / 下一篇（避免对布尔列使用 >/< 运算符）
    # 展示顺序：pinned desc -> published_at desc -> id desc
    # prev = 排名中更靠前的上一篇；next = 排名中更靠后的下一篇
    prev_conditions = [
        and_(
            Post.is_pinned == post.is_pinned,
            or_(
                Post.published_at > post.published_at,
                and_(Post.published_at == post.published_at, Post.id > post.id),
            ),
        )
    ]
    if not post.is_pinned:
        prev_conditions.append(Post.is_pinned.is_(True))

    next_conditions = [
        and_(
            Post.is_pinned == post.is_pinned,
            or_(
                Post.published_at < post.published_at,
                and_(Post.published_at == post.published_at, Post.id < post.id),
            ),
        )
    ]
    if post.is_pinned:
        next_conditions.append(Post.is_pinned.is_(False))

    prev_stmt = (
        select(Post)
        .where(Post.status == "published", or_(*prev_conditions))
        .order_by(Post.is_pinned.desc(), Post.published_at.desc(), Post.id.desc())
        .limit(1)
    )
    next_stmt = (
        select(Post)
        .where(Post.status == "published", or_(*next_conditions))
        .order_by(Post.is_pinned.asc(), Post.published_at.asc(), Post.id.asc())
        .limit(1)
    )

    prev_row = (await db.execute(prev_stmt)).scalar_one_or_none()
    next_row = (await db.execute(next_stmt)).scalar_one_or_none()

    prev_post = {"id": prev_row.id, "title": prev_row.title, "slug": prev_row.slug} if prev_row else None
    next_post = {"id": next_row.id, "title": next_row.title, "slug": next_row.slug} if next_row else None

    return success(
        {
            "post": _post_to_detail(post),
            "prev_post": prev_post,
            "next_post": next_post,
        }
    )


@router.get("/categories")
async def list_categories(db: AsyncSession = Depends(get_db)):
    """全部分类，含已发布文章计数"""
    count_subq = (
        select(func.count(Post.id))
        .where(Post.category_id == Category.id, Post.status == "published")
        .scalar_subquery()
    )
    result = await db.execute(select(Category, count_subq.label("post_count")))
    items = []
    for cat, cnt in result.all():
        data = schemas.CategoryOut.model_validate(cat).model_dump()
        data["post_count"] = cnt
        items.append(data)
    return success(items)


@router.get("/tags")
async def list_tags(db: AsyncSession = Depends(get_db)):
    """全部标签，含已发布文章计数"""
    count_subq = (
        select(func.count(Post.id))
        .join(post_tags)
        .where(post_tags.c.tag_id == Tag.id, Post.status == "published")
        .scalar_subquery()
    )
    result = await db.execute(select(Tag, count_subq.label("post_count")))
    items = []
    for tag, cnt in result.all():
        data = schemas.TagOut.model_validate(tag).model_dump()
        data["post_count"] = cnt
        items.append(data)
    return success(items)


@router.post("/posts")
async def create_post(
    payload: schemas.PostCreate,
    perms: Permissions = Depends(require_permission("can_create_post")),
    db: AsyncSession = Depends(get_db),
):
    """创建文章（需 can_create_post；若直接发布还需 can_publish_post）"""
    slug = await generate_unique_slug(db, payload.title)

    # 创建即发布需额外的发布权限
    if payload.status == "published" and not perms.can("can_publish_post"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权发布文章，请先保存为草稿")

    published_at = None
    if payload.status == "published":
        published_at = datetime.now(timezone.utc)

    summary = payload.summary
    if summary is None:
        summary = payload.content[:200]

    post = Post(
        title=payload.title,
        slug=slug,
        content=payload.content,
        summary=summary,
        cover_url=payload.cover_url,
        status=payload.status,
        is_pinned=payload.is_pinned,
        author_id=user.id,
        category_id=payload.category_id,
        published_at=published_at,
    )
    db.add(post)
    await db.flush()

    # 先加载关联集合，避免对全新对象赋值多对多关系时触发懒加载
    result = await db.execute(
        select(Post)
        .options(selectinload(Post.tags))
        .where(Post.id == post.id)
    )
    post = result.scalar_one()

    if payload.tags:
        tags_result = await db.execute(select(Tag).where(Tag.id.in_(payload.tags)))
        post.tags = list(tags_result.scalars().all())
    else:
        post.tags = []

    await db.commit()

    # 提交后重新加载完整关系，返回详情
    result = await db.execute(
        select(Post)
        .options(selectinload(Post.author), selectinload(Post.category), selectinload(Post.tags))
        .where(Post.id == post.id)
    )
    post = result.scalar_one()
    return success(_post_to_detail(post))


@router.put("/posts/{post_id}")
async def update_post(
    post_id: int,
    payload: schemas.PostUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    perms: Permissions = Depends(get_permissions),
):
    """编辑文章（自己的需 can_edit_own_post，他人的需 can_edit_others_post）"""
    result = await db.execute(
        select(Post)
        .options(selectinload(Post.tags))
        .where(Post.id == post_id)
    )
    post = result.scalar_one_or_none()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文章不存在")

    is_owner = post.author_id == user.id
    if not is_owner:
        # 非作者本人需 can_edit_others_post 权限
        perms.require("can_edit_others_post")
    else:
        # 作者本人需 can_edit_own_post 权限
        if not perms.can("can_edit_own_post"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权编辑自己的文章")

    if payload.title is not None:
        post.title = payload.title
        # 仅在用户未主动提供 slug 时重新生成（本接口无 slug 字段）
        post.slug = await generate_unique_slug(db, payload.title, exclude_id=post.id)
    if payload.content is not None:
        post.content = payload.content
        if payload.summary is None and post.summary is None:
            post.summary = payload.content[:200]
    if payload.summary is not None:
        post.summary = payload.summary
    if payload.cover_url is not None:
        post.cover_url = payload.cover_url
    if payload.category_id is not None:
        post.category_id = payload.category_id
    if payload.is_pinned is not None:
        post.is_pinned = payload.is_pinned
    if payload.tags is not None:
        tags_result = await db.execute(select(Tag).where(Tag.id.in_(payload.tags)))
        post.tags = list(tags_result.scalars().all())

    if payload.status is not None and payload.status != post.status:
        # 状态机：draft -> published -> archived
        # 已归档文章只有拥有 can_edit_others_post 权限的用户才能调整状态
        if post.status == "archived" and not perms.can("can_edit_others_post"):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="已归档文章不可修改状态")
        # 草稿转发布需 can_publish_post 权限
        if payload.status == "published" and post.status == "draft":
            if not perms.can("can_publish_post"):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权发布文章")
            if post.published_at is None:
                post.published_at = datetime.now(timezone.utc)
        post.status = payload.status

    post.updated_at = datetime.now(timezone.utc)
    await db.commit()
    result = await db.execute(
        select(Post)
        .options(selectinload(Post.author), selectinload(Post.category), selectinload(Post.tags))
        .where(Post.id == post.id)
    )
    post = result.scalar_one()
    return success(_post_to_detail(post))


@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    perms: Permissions = Depends(get_permissions),
):
    """删除文章（自己的需 can_delete_own_post，他人的需 can_delete_others_post）"""
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文章不存在")

    is_owner = post.author_id == user.id
    if not is_owner:
        perms.require("can_delete_others_post")
    else:
        if not perms.can("can_delete_own_post"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权删除自己的文章")

    await db.delete(post)
    await db.commit()
    return success(None)


@router.post("/categories")
async def create_category(
    payload: schemas.CategoryCreate,
    _: Permissions = Depends(require_permission("can_manage_categories")),
    db: AsyncSession = Depends(get_db),
):
    """创建分类（需 can_manage_categories）"""
    slug = payload.slug or payload.name.strip().lower().replace(" ", "-")
    existing = await db.execute(select(Category).where((Category.name == payload.name) | (Category.slug == slug)))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="分类名称或 slug 已存在")

    category = Category(name=payload.name, slug=slug, description=payload.description)
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return success(schemas.CategoryOut.model_validate(category).model_dump())


@router.put("/categories/{category_id}")
async def update_category(
    category_id: int,
    payload: schemas.CategoryUpdate,
    _: Permissions = Depends(require_permission("can_manage_categories")),
    db: AsyncSession = Depends(get_db),
):
    """更新分类（需 can_manage_categories）"""
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="分类不存在")

    if payload.name is not None:
        category.name = payload.name
    if payload.slug is not None:
        category.slug = payload.slug
    if payload.description is not None:
        category.description = payload.description

    await db.commit()
    await db.refresh(category)
    return success(schemas.CategoryOut.model_validate(category).model_dump())


@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: int,
    _: Permissions = Depends(require_permission("can_manage_categories")),
    db: AsyncSession = Depends(get_db),
):
    """删除分类（需 can_manage_categories），分类下有文章则禁止"""
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="分类不存在")

    post_count = (await db.execute(select(func.count(Post.id)).where(Post.category_id == category_id))).scalar() or 0
    if post_count > 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="该分类下存在文章，无法删除",
        )

    await db.delete(category)
    await db.commit()
    return success(None)


@router.post("/tags")
async def create_tag(
    payload: schemas.TagCreate,
    _: Permissions = Depends(require_permission("can_manage_tags")),
    db: AsyncSession = Depends(get_db),
):
    """创建标签（需 can_manage_tags）"""
    slug = payload.slug or payload.name.strip().lower().replace(" ", "-")
    existing = await db.execute(select(Tag).where((Tag.name == payload.name) | (Tag.slug == slug)))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="标签名称或 slug 已存在")

    tag = Tag(name=payload.name, slug=slug)
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return success(schemas.TagOut.model_validate(tag).model_dump())


@router.delete("/tags/{tag_id}")
async def delete_tag(
    tag_id: int,
    _: Permissions = Depends(require_permission("can_manage_tags")),
    db: AsyncSession = Depends(get_db),
):
    """删除标签（需 can_manage_tags）"""
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="标签不存在")

    await db.delete(tag)
    await db.commit()
    return success(None)
