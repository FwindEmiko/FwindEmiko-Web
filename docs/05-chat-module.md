# 05 — AI 对话模块（LLM 占位）

> **依赖**: `01-backend-core.md`  
> **目标**: 对话会话管理 + 消息存储 + SSE 流式 API（**LLM 实际调用留空，后面星玖接**）  
> **验证**: 能创建会话、发送消息、收到 mock 回复（或空回复）

---

## 1. 设计要点

这个模块目前做**骨架**，不接真实 LLM。后端完成：
- 对话 CRUD（会话列表 + 历史消息）
- SSE 端点框架（能流式返回数据，但内容暂为 mock）
- 登录验证 + 每日配额检查

真实 LLM（Ollama / Hermes）由星玖后续接入 `backend/app/modules/chat/llm_client.py`。

---

## 2. 数据模型 (`backend/app/modules/chat/models.py`)

```python
class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id: int (PK)
    user_id: int (FK → users.id, ondelete CASCADE)
    title: str (default "新对话")      # 自动从第一条用户消息截取
    model: str (default "ollama")       # 预留: ollama / hermes / cloud
    message_count: int (default 0)
    created_at: datetime
    updated_at: datetime

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id: int (PK)
    session_id: int (FK → chat_sessions.id, ondelete CASCADE)
    role: str                           # user / assistant / system
    content: str
    tokens_used: int (default 0)
    created_at: datetime
```

---

## 3. API 端点

### 会话管理（需登录）

```
GET  /api/chat/sessions
  返回当前用户的对话列表，按 updated_at DESC
  返回: [{id, title, model, message_count, created_at, updated_at}, ...]

POST /api/chat/sessions
  body: {title?: "新对话"}
  返回新会话对象

GET  /api/chat/sessions/{id}/messages
  返回该会话所有消息，按 created_at ASC
  返回: [{id, role, content, created_at}, ...]

DELETE /api/chat/sessions/{id}
  逻辑: 删除会话 + 所有消息
  权限: 只能删自己的（或 admin 可删全部）
```

### 发送消息（需登录）⚠️ 核心接口

```
POST /api/chat/sessions/{id}/messages
  body: {
    "content": "用户的问题",
    "model?": "ollama"          # 可切换模型（预留）
  }
  
  逻辑:
    1. 检查每日配额 (默认 50 次/天, admin 不限)
    2. 保存 user 消息 (role=user)
    3. 调用 LLM（目前返回 mock 回复或空占位）
    4. 保存 assistant 消息 (role=assistant)
    5. 通过 SSE 流式返回

  Content-Type: text/event-stream
  
  SSE 数据流格式:
    data: {"type":"chunk","content":"你"}\n\n
    data: {"type":"chunk","content":"好"}\n\n
    data: {"type":"done","message_id":123}\n\n
    data: {"type":"error","message":"配额已用完"}\n\n
```

---

## 4. LLM 客户端占位 (`backend/app/modules/chat/llm_client.py`)

```python
# ⚠️ 这是占位代码——后续星玖接入真实 LLM 时替换此文件

from typing import AsyncGenerator
from app.config import settings

async def stream_chat(
    model: str,
    messages: list[dict],   # [{"role":"user","content":"..."}, ...]
    system_prompt: str | None = None
) -> AsyncGenerator[str, None]:
    """
    流式对话生成器。
    
    当前为占位模式：返回一条 mock 消息后结束。
    
    未来接入方式:
      - Ollama: POST {settings.OLLAMA_BASE_URL}/api/chat → stream JSON lines
      - Hermes: POST {settings.HERMES_API_URL}/chat → stream SSE
      - Cloud Agent: 类似
    
    返回: AsyncGenerator 逐 token yield 字符串内容
    """
    if settings.LLM_BACKEND == "none" or settings.LLM_BACKEND == "mock":
        # Mock 模式: 返回占位回复
        yield "这是一个占位回复。AI 对话功能尚未接入 LLM，请联系星玖完成部署。"
        return
    
    # === 真实 LLM 接入点 ===
    # 以下代码结构供参考，实际接入时星玖会修改:
    #
    # async with httpx.AsyncClient() as client:
    #     async with client.stream("POST", f"{settings.OLLAMA_BASE_URL}/api/chat",
    #         json={"model": model, "messages": messages, "stream": True}
    #     ) as resp:
    #         async for line in resp.aiter_lines():
    #             if line:
    #                 yield json.loads(line)["message"]["content"]
    
    yield "LLM 未配置。"
```

---

## 5. 配额系统 (`backend/app/modules/chat/service.py`)

```python
from datetime import date

# 每日配额 key: chat_quota:{user_id}:{date}
# 用 Redis 计数 或 数据库表 chat_quota (user_id, date, count)

async def check_quota(user: User) -> bool:
    """检查用户今日配额是否用完。admin 不限。"""
    if user.role == "admin":
        return True
    
    today = date.today()
    # 查询今日已用次数
    used = await count_today_messages(user.id)
    return used < 50   # 50 次/天

async def increment_quota(user: User):
    """递增今日使用计数。"""
```

建议用数据库表（简单，不依赖 Redis）：

```python
class ChatQuota(Base):
    __tablename__ = "chat_quotas"
    id: int (PK)
    user_id: int (FK)
    date: date
    count: int (default 0)
    # unique: (user_id, date)
```

---

## 6. SSE 端点实现要点

```python
# backend/app/modules/chat/router.py

@router.post("/chat/sessions/{session_id}/messages")
async def send_message(
    session_id: int,
    body: ChatMessageCreate,
    user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    # 1. 验证会话归属
    # 2. 配额检查
    # 3. 保存用户消息
    # 4. 调用 llm_client.stream_chat()
    # 5. 使用 StreamingResponse 返回 SSE

    async def event_generator():
        full_content = ""
        async for chunk in stream_chat(body.model, messages):
            full_content += chunk
            yield f"data: {json.dumps({'type':'chunk','content':chunk})}\n\n"
        
        # 保存 assistant 消息
        msg = await save_assistant_message(db, session_id, full_content)
        yield f"data: {json.dumps({'type':'done','message_id':msg.id})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Nginx 禁用缓冲
        }
    )
```

---

## 7. 验证方式

```bash
# 1. 创建对话
curl -X POST http://localhost:8000/api/chat/sessions \
  -H "Authorization: Bearer *** \
  -d '{}'
# 返回: {"code":0,"data":{"id":1,"title":"新对话"}}

# 2. 发送消息（注意：这是 SSE，curl 用 -N 不缓冲）
curl -N -X POST http://localhost:8000/api/chat/sessions/1/messages \
  -H "Authorization: Bearer *** \
  -H "Content-Type: application/json" \
  -d '{"content":"你好"}'
# 应看到流式 SSE 输出（mock 回复）

# 3. 查看历史
curl http://localhost:8000/api/chat/sessions/1/messages \
  -H "Authorization: Bearer ***
```

---

## 8. 灵活性留白

- **LLM 后端切换**: `LLM_BACKEND` 环境变量控制，值为 `none|mock|ollama|hermes|cloud`。`llm_client.py` 根据此值选不同的生成器实现。
- **系统提示词**: 星玖后续接入时会设置 System Prompt（角色定义）。先预留一个 `system_prompt` 参数在 `stream_chat` 里。
- **消息截断**: 长对话历史需要截断。建议保留最近 20 条消息 + System Prompt，超出部分做摘要或丢弃。
- **配额存储**: 用数据库表即可。不需要 Redis（减少依赖）。每月 1 日清理旧记录。
- **会话标题自动生成**: 第一条用户消息的前 30 个字符作为 `title`。

---

> **下一份**: `06-frontend-nuxt.md` — Nuxt3 公网站点
