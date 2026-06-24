# LLM 客户端占位
from typing import AsyncGenerator

from app.config import settings


async def stream_chat(
    model: str,
    messages: list[dict],
    system_prompt: str | None = None,
) -> AsyncGenerator[str, None]:
    """
    流式对话生成器（占位实现）。

    当前根据 settings.LLM_BACKEND 返回 mock 回复；后续可接入 Ollama / Hermes / Cloud。
    """
    backend = getattr(settings, "LLM_BACKEND", "mock").lower()

    if backend in ("none", "mock", ""):
        yield "这是一个占位回复。AI 对话功能尚未接入真实 LLM，请联系星玖完成部署。"
        return

    # === 真实 LLM 接入点（后续由星玖实现） ===
    yield f"LLM 后端 '{backend}' 尚未实现。"
