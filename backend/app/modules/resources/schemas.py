# 资源展示模块请求/响应模型
import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ResourceBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    type: str = Field(..., pattern="^(plugin|mod|datapack|tool)$")
    game_versions: list[str] = Field(default_factory=list)
    loaders: list[str] = Field(default_factory=list)
    icon_url: str | None = Field(None, max_length=500)
    cover_url: str | None = Field(None, max_length=500)


class ResourceCreate(ResourceBase):
    pass


class ResourceUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, min_length=1)
    type: str | None = Field(None, pattern="^(plugin|mod|datapack|tool)$")
    game_versions: list[str] | None = None
    loaders: list[str] | None = None
    icon_url: str | None = Field(None, max_length=500)
    cover_url: str | None = Field(None, max_length=500)
    status: str | None = Field(None, pattern="^(draft|published)$")


class ResourceVersionBase(BaseModel):
    version_string: str = Field(..., min_length=1, max_length=100)
    changelog: str | None = Field(None, max_length=5000)
    file_url: str | None = Field(None, max_length=500)
    external_url: str | None = Field(None, max_length=500)
    # 下载方式：local=本站上传 / external=外链网盘
    download_type: str = Field("local", pattern="^(local|external)$")
    # 外链网盘标签（如 "百度网盘"），仅 external 时使用
    external_label: str | None = Field(None, max_length=100)
    file_size: int | None = Field(None, ge=0)
    file_hash: str | None = Field(None, max_length=128)
    is_prerelease: bool = False

    @model_validator(mode="after")
    def check_url(self):
        # local 类型必须有 file_url，external 类型必须有 external_url
        if self.download_type == "external":
            if not self.external_url:
                raise ValueError("外链下载方式必须提供 external_url")
        else:  # local
            if not self.file_url:
                raise ValueError("本站下载方式必须提供 file_url")
        return self


class ResourceVersionCreate(ResourceVersionBase):
    pass


class ResourceVersionUpdate(BaseModel):
    version_string: str | None = Field(None, min_length=1, max_length=100)
    changelog: str | None = Field(None, max_length=5000)
    file_url: str | None = Field(None, max_length=500)
    external_url: str | None = Field(None, max_length=500)
    download_type: str | None = Field(None, pattern="^(local|external)$")
    external_label: str | None = Field(None, max_length=100)
    file_size: int | None = Field(None, ge=0)
    file_hash: str | None = Field(None, max_length=128)
    is_prerelease: bool | None = None


class ResourceVersionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    resource_id: int
    version_string: str
    changelog: str | None
    file_url: str | None
    external_url: str | None
    download_type: str
    external_label: str | None
    file_size: int | None
    file_hash: str | None
    downloads: int
    is_prerelease: bool
    created_at: datetime


class ScreenshotOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    resource_id: int
    image_url: str
    thumb_url: str | None
    caption: str | None
    sort_order: int


class ResourceListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str
    description: str
    type: str
    game_versions: list[str]
    loaders: list[str]
    icon_url: str | None
    cover_url: str | None
    download_count: int
    status: str
    created_at: datetime
    updated_at: datetime
    latest_version: ResourceVersionOut | None = None

    @field_validator("game_versions", "loaders", mode="before")
    @classmethod
    def _parse_json_list(cls, v):
        if isinstance(v, str):
            return parse_json_list(v)
        return v


class ResourceDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str
    description: str
    type: str
    game_versions: list[str]
    loaders: list[str]
    icon_url: str | None
    cover_url: str | None
    download_count: int
    status: str
    created_at: datetime
    updated_at: datetime
    versions: list[ResourceVersionOut]
    screenshots: list[ScreenshotOut]

    @field_validator("game_versions", "loaders", mode="before")
    @classmethod
    def _parse_json_list(cls, v):
        if isinstance(v, str):
            return parse_json_list(v)
        return v


class PaginatedResources(BaseModel):
    items: list[ResourceListItem]
    total: int
    page: int
    size: int
    pages: int


class ScreenshotReorder(BaseModel):
    screenshot_ids: list[int]


def parse_json_list(value: str | list | None) -> list[str]:
    if not value:
        return []
    if isinstance(value, list):
        return [str(x) for x in value]
    try:
        data = json.loads(value)
        return [str(x) for x in data] if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def dump_json_list(value: list[str]) -> str:
    return json.dumps(value, ensure_ascii=False)
