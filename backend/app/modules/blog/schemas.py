# 博客模块请求/响应模型
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    slug: str | None = Field(None, max_length=100)
    description: str | None = Field(None, max_length=2000)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    slug: str | None = Field(None, max_length=100)
    description: str | None = Field(None, max_length=2000)


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    description: str | None
    created_at: datetime
    post_count: int = 0


class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    slug: str | None = Field(None, max_length=100)


class TagCreate(TagBase):
    pass


class TagOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    created_at: datetime
    post_count: int = 0


class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    summary: str | None = Field(None, max_length=1000)
    cover_url: str | None = Field(None, max_length=500)
    category_id: int | None = None
    tags: list[int] | None = None
    status: str = Field("draft", pattern="^(draft|published|archived)$")
    is_pinned: bool = False


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    content: str | None = Field(None, min_length=1)
    summary: str | None = Field(None, max_length=1000)
    cover_url: str | None = Field(None, max_length=500)
    category_id: int | None = None
    tags: list[int] | None = None
    status: str | None = Field(None, pattern="^(draft|published|archived)$")
    is_pinned: bool | None = None


class AuthorBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    display_name: str | None


class CategoryBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str


class TagBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str


class PostListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str
    summary: str | None
    cover_url: str | None
    status: str
    is_pinned: bool
    view_count: int
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime
    author: AuthorBrief
    category: CategoryBrief | None
    tags: list[TagBrief]


class PostDetail(PostListItem):
    content_md: str
    content_html: str


class PostDetailResponse(BaseModel):
    post: PostDetail
    prev_post: dict[str, Any] | None
    next_post: dict[str, Any] | None


class PaginatedPosts(BaseModel):
    items: list[PostListItem]
    total: int
    page: int
    size: int
    pages: int
