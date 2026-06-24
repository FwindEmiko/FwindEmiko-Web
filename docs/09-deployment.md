# 09 — 部署参考

> **注意**: 部署由星玖负责。此文档供 Trae AI 了解部署架构和约束，方便在开发中做出兼容性决策。  
> **部署时机**: Trae 完成代码后，星玖接手 Docker 编排 + Nginx 配置 + 生产上线。

---

## 1. 部署目标

| 组件 | 部署位置 | 说明 |
|------|----------|------|
| Nginx | 阿里云 ECS | 反代 + SSL 终结 + 静态文件 |
| FastAPI Backend | 阿里云 ECS (Docker) | uvicorn |
| Nuxt3 SSR | 阿里云 ECS (Docker) | Node.js 运行时 |
| Admin SPA | 阿里云 ECS (静态文件) | `vite build` → Nginx serve |
| MySQL | 阿里云 ECS (Docker) | 数据持久卷 |
| Ollama (LLM) | 汐汐酱本地 PC | RTX 4090, 后续星玖接入 |
| ChromaDB (RAG) | 汐汐酱本地 PC | 后续星玖接入 |

---

## 2. Docker Compose（生产）

```yaml
# docker-compose.yml
services:
  nginx:
    image: nginx:alpine
    ports: ['80:80', '443:443']
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro               # SSL 证书
      - admin_dist:/var/www/admin:ro           # Admin SPA 构建产物
      - uploads:/var/www/uploads:ro            # 上传文件（只读）
    depends_on: [backend, nuxt]

  backend:
    build: ./backend
    expose: [8000]
    env_file: .env
    volumes: [uploads:/app/uploads]
    depends_on: [mysql]
    restart: unless-stopped

  nuxt:
    build: ./nuxt-app
    expose: [3000]
    env_file: .env
    restart: unless-stopped

  mysql:
    image: mysql:8.0
    volumes: [mysql_data:/var/lib/mysql]
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASS}
      MYSQL_DATABASE: windemiko
    command: >
      --character-set-server=utf8mb4
      --collation-server=utf8mb4_unicode_ci
      --default-authentication-plugin=mysql_native_password
    restart: unless-stopped

volumes:
  mysql_data:
  uploads:
  admin_dist:
```

---

## 3. Nginx 配置要点

```nginx
server {
    listen 443 ssl http2;
    server_name f.windemiko.top;

    # SSL 证书
    ssl_certificate     /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;

    # 上传限制
    client_max_body_size 500M;

    # === Admin SPA ===
    location /admin {
        alias /var/www/admin;
        try_files $uri $uri/ /admin/index.html;
        # Admin 是 CSR，所有子路由都 fallback 到 index.html
    }

    # === API ===
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # SSE 支持（AI 对话流式响应）
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 120s;
    }

    # === 文件直链 ===
    location /files/ {
        alias /var/www/uploads/;
        # 可根据需要添加认证（下载接口已做权限校验）
    }

    # === Nuxt3 SSR ===
    location / {
        proxy_pass http://nuxt:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# HTTP → HTTPS 重定向
server {
    listen 80;
    server_name f.windemiko.top;
    return 301 https://$host$request_uri;
}
```

### 关键注意

- Admin SPA 用 `alias` 而不是 `root`。`try_files` 确保 Vue Router 的 history 模式正常工作。
- SSE 必须关闭 `proxy_buffering`，否则流式响应会被缓冲直到完成。
- 文件上传 `client_max_body_size` 设 500MB，匹配后端 `MAX_UPLOAD_SIZE`。

---

## 3.1 宿主机 Nginx → Admin 容器代理（生产）

生产环境使用 `docker-compose.prod.yml`，Admin SPA 运行在 `fwe-admin` 容器（端口 4175）。
Admin 构建时 `vite.config.ts` 设置了 `base: '/admin/'`，因此通过目录路径 `/admin/` 访问。

在 ECS 宿主机 nginx 配置（`/www/MiragEdge/MiragEdge-DocWeb/.DockerCompose/default.conf`）中添加以下 location，将 `/admin/` 代理到 admin 容器：

```nginx
# === Admin SPA → fwe-admin 容器 ===
location /admin/ {
    proxy_pass http://fwe-admin:80;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

> **说明**：
> - `proxy_pass http://fwe-admin:80;` 不带尾部路径，URI 原样传递（含 `/admin/` 前缀）。
> - admin 容器内 nginx（`admin-nginx.conf`）通过 `alias` 将 `/admin/` 映射到静态文件目录。
> - Admin 使用 `createWebHashHistory`，路由形如 `/admin/#/dashboard`，hash 部分不经过服务器。
> - API 请求使用相对路径 `/api`，由宿主机 nginx 的 `/api/` location 统一代理到后端。
> - 前端登录后 `access_token` 存入 localStorage，打开 `/admin/` 时 admin-spa 读取同一 key 自动恢复登录态（统一登录）。

---

## 4. Dockerfile 示例

### Backend (`backend/Dockerfile`)

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p /app/uploads
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Nuxt3 (`nuxt-app/Dockerfile`)

```dockerfile
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile
COPY . .
RUN pnpm build

FROM node:22-alpine
WORKDIR /app
COPY --from=build /app/.output ./.output
EXPOSE 3000
CMD ["node", ".output/server/index.mjs"]
```

### Admin SPA

不设独立容器——构建产物直接挂载到 Nginx：

```bash
cd admin-spa
pnpm build
# 产出 dist/ → 挂载到 Nginx 的 /var/www/admin
```

---

## 5. 环境变量（生产 `.env`）

```env
DATABASE_URL=mysql+aiomysql://windemiko:${DB_PASS}@mysql:3306/windemiko
JWT_SECRET=${随机生成，≥ 32 字符}
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_EXPIRE_DAYS=7
UPLOAD_DIR=/app/uploads
MAX_UPLOAD_SIZE=524288000
CORS_ORIGINS=https://f.windemiko.top
DEBUG=false
LLM_BACKEND=none
APP_NAME=WindEmiko Portal
```

---

## 6. 旧服务迁移

```bash
# 1. cloud.miragedge.top → 301 重定向到新站下载页
#    （在 ESA 控制台配置 URL 重写规则）

# 2. WordPress 文章迁移
#    使用 scripts/migrate-wp.ts 脚本
#    从 WP 导出 XML → 解析 → POST /api/posts
```

---

## 7. 备份策略

```bash
# 数据库每日备份（cron）
0 3 * * * docker exec mysql mysqldump -u root windemiko | gzip > /backup/db_$(date +\%Y\%m\%d).sql.gz

# 文件热备（rsync）
0 4 * * * rsync -a /var/lib/docker/volumes/windemiko_uploads/ /backup/uploads/

# 保留最近 30 天
```

---

## 8. 灵活性留白

- SSL 证书：可用 Let's Encrypt certbot 自动续签，或阿里云免费证书。
- CDN：阿里云 ESA 全站加速套到域名上，配置好源站即可。
- 扩展性：日后面向高并发可直接加 `replicas: 3` 给 backend/nuxt，前面 Nginx 做负载均衡。
- 图床：截图和上传文件可后续迁到阿里云 OSS + CDN，减轻 ECS 带宽压力。

---

> **全文完。** 10 份开发者文档全部就绪。  
> **下一步**: 汐汐酱把文档和方案书给 Trae AI，开始编码。  
> **星玖下一步**: 部署 + LLM 接入 + Live2D 星玖模型替换。
