# 用户认证模型
from datetime import datetime, timezone

from sqlalchemy import Integer, String, Boolean, DateTime, Text, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    role: Mapped[str] = mapped_column(String(20), default="member", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        Index("ix_users_username_email", "username", "email"),
    )


# 角色权限字段名清单（用于反射、序列化、迁移 seed）
# 与 RolePermission 模型中 mapped_column 的权限列保持一致
ROLE_PERMISSION_FIELDS: tuple[str, ...] = (
    # 文章
    "can_create_post",
    "can_edit_own_post",
    "can_delete_own_post",
    "can_publish_post",
    "can_edit_others_post",
    "can_delete_others_post",
    # 资源
    "can_create_resource",
    "can_edit_own_resource",
    "can_delete_own_resource",
    "can_publish_resource",
    "can_edit_others_resource",
    "can_delete_others_resource",
    # 下载/文件
    "can_upload_file",
    "can_download_file",
    "can_delete_file",
    "can_manage_folders",
    # 分类/标签
    "can_manage_categories",
    "can_manage_tags",
    # 用户管理
    "can_view_users",
    "can_manage_users",
    # AI 对话
    "can_use_chat",
    # 管理员
    "can_access_admin",
)


class RolePermission(Base):
    """角色细粒度权限矩阵

    每行代表一个角色（admin / author / moderator / member / guest）的全部权限。
    权限以布尔列形式存储，便于在管理后台用 Switch 开关直接编辑。
    """

    __tablename__ = "role_permissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    role: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)

    # 文章
    can_create_post: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_edit_own_post: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_delete_own_post: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_publish_post: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_edit_others_post: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_delete_others_post: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # 资源
    can_create_resource: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_edit_own_resource: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_delete_own_resource: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_publish_resource: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_edit_others_resource: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_delete_others_resource: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # 下载/文件
    can_upload_file: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_download_file: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_delete_file: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_manage_folders: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # 分类/标签
    can_manage_categories: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_manage_tags: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # 用户管理
    can_view_users: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_manage_users: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # AI 对话
    can_use_chat: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    chat_daily_limit: Mapped[int] = mapped_column(Integer, default=20, nullable=False)

    # 管理员
    can_access_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
