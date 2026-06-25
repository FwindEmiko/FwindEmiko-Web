# 后端全局配置管理
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置，优先从 .env 文件读取"""

    # 数据库
    DATABASE_URL: str

    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24h
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # 文件上传
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 524288000  # 500MB
    AVATAR_MAX_SIZE: int = 2097152  # 2MB

    # CORS
    CORS_ORIGINS: list[str] = ["*"]

    # LLM
    LLM_BACKEND: str = "mock"  # none | mock | ollama | hermes | cloud

    # 应用
    APP_NAME: str = "WindEmiko Portal"
    DEBUG: bool = True

    # 注册默认角色（在 .env 中配置，影响通过 /auth/register 接口新建用户的角色）
    # 可选值：member / author / moderator（admin 不能通过注册接口创建）
    REGISTER_DEFAULT_ROLE: str = "member"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
