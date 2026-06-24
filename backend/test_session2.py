# Session 2 自测脚本（httpx 执行，输出等效 curl 命令与结果）
import asyncio
import json
import os
from datetime import datetime, timezone

import httpx

BASE = "http://localhost:8002"


async def ensure_user_roles():
    """确保测试账号角色正确"""
    from sqlalchemy import select
    from app.database import AsyncSessionLocal
    from app.modules.auth.models import User
    from app.core.security import hash_password

    async with AsyncSessionLocal() as db:
        targets = [
            ("admin_user", "admin"),
            ("author_user", "author"),
            ("member_user", "member"),
        ]
        for username, role in targets:
            result = await db.execute(select(User).where(User.username == username))
            user = result.scalar_one_or_none()
            if user is None:
                user = User(
                    username=username,
                    email=f"{role}@test.com",
                    password_hash=hash_password("Password123"),
                    role=role,
                )
                db.add(user)
            else:
                user.role = role
        await db.commit()


asyncio.run(ensure_user_roles())


def log(name: str, curl: str, resp: httpx.Response):
    print(f"\n=== {name} ===")
    print("curl command:")
    print(curl)
    print(f"status: {resp.status_code}")
    try:
        print("response:", json.dumps(resp.json(), ensure_ascii=False, indent=2)[:1500])
    except Exception:
        print("response:", resp.text[:1500])


def json_body(obj: dict) -> str:
    return json.dumps(obj, ensure_ascii=False).replace('"', '\\"')


def ensure_category(client, admin_auth):
    r = client.get("/api/categories")
    for item in r.json().get("data", []):
        if item["slug"] == "tech":
            return item["id"]
    r = client.post(
        "/api/categories",
        json={"name": "技术笔记", "slug": "tech"},
        headers=admin_auth,
    )
    return r.json()["data"]["id"]


def ensure_tag(client, author_auth):
    r = client.get("/api/tags")
    for item in r.json().get("data", []):
        if item["slug"] == "fastapi":
            return item["id"]
    r = client.post(
        "/api/tags",
        json={"name": "FastAPI", "slug": "fastapi"},
        headers=author_auth,
    )
    return r.json()["data"]["id"]


def main():
    client = httpx.Client(base_url=BASE, timeout=30)

    # 准备账号
    users = {
        "admin": {"username": "admin_user", "password": "Password123", "role": "admin"},
        "author": {"username": "author_user", "password": "Password123", "role": "author"},
        "member": {"username": "member_user", "password": "Password123", "role": "member"},
    }
    for role, u in users.items():
        r = client.post(
            "/api/auth/register",
            json={"username": u["username"], "email": f"{role}@test.com", "password": u["password"]},
        )
        if r.status_code == 200:
            print(f"registered {role}")
        else:
            try:
                msg = r.json().get("message")
            except Exception:
                msg = r.text
            print(f"register {role}:", r.status_code, msg)

    tokens = {}
    for role, u in users.items():
        r = client.post("/api/auth/login", json={"username": u["username"], "password": u["password"]})
        tokens[role] = r.json()["data"]["access_token"]
        print(f"login {role}: ok")

    def auth(role: str) -> dict:
        return {"Authorization": f"Bearer {tokens[role]}"}

    # === 博客模块 ===
    cat_id = ensure_category(client, auth("admin"))
    tag_id = ensure_tag(client, auth("author"))
    print(f"category_id={cat_id}, tag_id={tag_id}")

    post = client.post(
        "/api/posts",
        json={
            "title": "Session2 测试文章",
            "content": "# 标题\n\n这是正文。",
            "status": "published",
            "category_id": cat_id,
            "tags": [tag_id],
        },
        headers=auth("author"),
    )
    log(
        "创建文章",
        f'curl -X POST {BASE}/api/posts -H "Authorization: Bearer <author_token>" -H "Content-Type: application/json" -d "{json_body({"title":"Session2 测试文章","content":"# 标题\\n\\n这是正文。","status":"published","category_id":cat_id,"tags":[tag_id]})}"',
        post,
    )
    post_id = post.json()["data"]["id"]
    post_slug = post.json()["data"]["slug"]

    put = client.put(f"/api/posts/{post_id}", json={"title": "Session2 已更新"}, headers=auth("author"))
    log(
        "编辑文章",
        f'curl -X PUT {BASE}/api/posts/{post_id} -H "Authorization: Bearer <author_token>" -H "Content-Type: application/json" -d "{json_body({"title":"Session2 已更新"})}"',
        put,
    )
    # 编辑后 slug 可能变化，用返回的新 slug 查详情
    post_slug = put.json()["data"]["slug"]

    lst = client.get("/api/posts", params={"category": "tech", "tag": "fastapi", "q": "Session2"})
    log("文章搜索列表", f'curl "{BASE}/api/posts?category=tech&tag=fastapi&q=Session2"', lst)

    detail = client.get(f"/api/posts/{post_slug}")
    log("文章详情", f'curl "{BASE}/api/posts/{post_slug}"', detail)

    del_post = client.delete(f"/api/posts/{post_id}", headers=auth("admin"))
    log(
        "删除文章",
        f'curl -X DELETE {BASE}/api/posts/{post_id} -H "Authorization: Bearer <admin_token>"',
        del_post,
    )

    # === 资源模块 ===
    resource_title = f"SkyIslandHome-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    resource_slug = resource_title.lower().replace(" ", "-")
    resource = client.post(
        "/api/resources",
        json={
            "title": resource_title,
            "type": "plugin",
            "game_versions": ["1.21.11"],
            "loaders": ["Paper"],
            "description": "空岛家园系统",
        },
        headers=auth("author"),
    )
    log(
        "创建资源",
        f'curl -X POST {BASE}/api/resources -H "Authorization: Bearer <author_token>" -H "Content-Type: application/json" -d "{json_body({"title":resource_title,"type":"plugin","game_versions":["1.21.11"],"loaders":["Paper"],"description":"空岛家园系统"})}"',
        resource,
    )
    res_id = resource.json()["data"]["id"]

    client.put(f"/api/resources/{res_id}", json={"status": "published"}, headers=auth("admin"))

    version = client.post(
        f"/api/resources/{res_id}/versions",
        json={"version_string": "v1.2.0", "external_url": "https://example.com/download"},
        headers=auth("author"),
    )
    log(
        "添加版本",
        f'curl -X POST {BASE}/api/resources/{res_id}/versions -H "Authorization: Bearer <author_token>" -H "Content-Type: application/json" -d "{json_body({"version_string":"v1.2.0","external_url":"https://example.com/download"})}"',
        version,
    )

    here = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(here, "uploads", "test_screenshot.png")
    os.makedirs(os.path.dirname(img_path), exist_ok=True)
    from PIL import Image

    img = Image.new("RGB", (800, 600), color=(73, 109, 137))
    img.save(img_path)
    with open(img_path, "rb") as f:
        shot = client.post(
            f"/api/resources/{res_id}/screenshots",
            files={"files": ("test.png", f, "image/png")},
            headers=auth("author"),
        )
    log(
        "上传截图",
        f'curl -X POST {BASE}/api/resources/{res_id}/screenshots -H "Authorization: Bearer <author_token>" -F "files=@test.png"',
        shot,
    )

    res_detail = client.get(f"/api/resources/{resource_slug}")
    log("资源详情", f'curl "{BASE}/api/resources/{resource_slug}"', res_detail)

    # === 下载站模块 ===
    suffix = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    public_slug = f"public-{suffix}"
    public_folder = client.post(
        "/api/downloads/folders",
        json={"name": "公开资源", "slug": public_slug, "is_visible": True},
        headers=auth("admin"),
    )
    log(
        "创建公开文件夹",
        f'curl -X POST {BASE}/api/downloads/folders -H "Authorization: Bearer <admin_token>" -H "Content-Type: application/json" -d "{json_body({"name":"公开资源","slug":public_slug,"is_visible":True})}"',
        public_folder,
    )
    public_id = public_folder.json()["data"]["id"]

    vip_slug = f"vip-{suffix}"
    vip_folder = client.post(
        "/api/downloads/folders",
        json={
            "name": "VIP资源",
            "slug": vip_slug,
            "is_visible": True,
            "permission_rules": [
                {"role": "guest", "can_read": False, "can_download": False},
                {"role": "member", "can_read": True, "can_download": True},
            ],
        },
        headers=auth("admin"),
    )
    log(
        "创建受限文件夹",
        f'curl -X POST {BASE}/api/downloads/folders -H "Authorization: Bearer <admin_token>" -H "Content-Type: application/json" -d "{json_body({"name":"VIP资源","slug":vip_slug,"is_visible":True,"permission_rules":[{"role":"guest","can_read":False,"can_download":False},{"role":"member","can_read":True,"can_download":True}]})}"',
        vip_folder,
    )

    tree_guest = client.get("/api/downloads/folders")
    log("未登录文件夹树", f'curl "{BASE}/api/downloads/folders"', tree_guest)

    tree_member = client.get("/api/downloads/folders", headers=auth("member"))
    log("member 文件夹树", f'curl "{BASE}/api/downloads/folders" -H "Authorization: Bearer <member_token>"', tree_member)

    test_file = os.path.join(here, "uploads", "test_download.txt")
    with open(test_file, "w") as f:
        f.write("hello downloads")
    with open(test_file, "rb") as f:
        up = client.post(
            "/api/downloads/files",
            params={"folder_id": public_id},
            files={"files": ("test_download.txt", f, "text/plain")},
            headers=auth("admin"),
        )
    log(
        "上传文件",
        f'curl -X POST "{BASE}/api/downloads/files?folder_id={public_id}" -H "Authorization: Bearer <admin_token>" -F "files=@test_download.txt"',
        up,
    )

    # === AI 对话模块 ===
    sess = client.post("/api/chat/sessions", json={}, headers=auth("member"))
    log(
        "创建会话",
        f'curl -X POST {BASE}/api/chat/sessions -H "Authorization: Bearer <member_token>" -H "Content-Type: application/json" -d "{{}}"',
        sess,
    )
    session_id = sess.json()["data"]["id"]

    print(f"\n=== SSE 发送消息 (session {session_id}) ===")
    print(
        f'curl -N -X POST {BASE}/api/chat/sessions/{session_id}/messages -H "Authorization: Bearer <member_token>" -H "Content-Type: application/json" -d "{json_body({"content":"你好"})}"'
    )
    with client.stream(
        "POST",
        f"/api/chat/sessions/{session_id}/messages",
        json={"content": "你好"},
        headers=auth("member"),
    ) as stream:
        for line in stream.iter_lines():
            print("SSE:", line)

    hist = client.get(f"/api/chat/sessions/{session_id}/messages", headers=auth("member"))
    log(
        "查看历史",
        f'curl {BASE}/api/chat/sessions/{session_id}/messages -H "Authorization: Bearer <member_token>"',
        hist,
    )

    quota = client.get("/api/chat/quota", headers=auth("member"))
    log(
        "查看配额",
        f'curl {BASE}/api/chat/quota -H "Authorization: Bearer <member_token>"',
        quota,
    )

    client.close()


if __name__ == "__main__":
    main()
