# 本地开发指南

在不使用 Docker 的情况下运行 GPT-Researcher 后端。

## 方案一：完整环境（PostgreSQL + Redis）

### 前置要求

- Python 3.10+
- PostgreSQL 14+
- Redis 6+ (可选，用于 Celery)

### 1. 安装系统依赖

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv postgresql redis-server
```

**macOS:**
```bash
brew install python3 postgresql redis
```

**Windows:**
- 安装 [Python](https://www.python.org/downloads/)
- 安装 [PostgreSQL](https://www.postgresql.org/download/windows/)
- 安装 [Redis](https://github.com/microsoftarchive/redis/releases)

### 2. 配置 PostgreSQL

```bash
# 启动 PostgreSQL 服务
sudo service postgresql start  # Linux
brew services start postgresql  # macOS

# 创建数据库和用户
sudo -u postgres psql

# 在 psql 中执行:
CREATE USER gpt_researcher WITH PASSWORD 'gpt_researcher_pass';
CREATE DATABASE gpt_researcher OWNER gpt_researcher;
GRANT ALL PRIVILEGES ON DATABASE gpt_researcher TO gpt_researcher;
\q
```

### 3. 配置 Redis（可选）

```bash
# 启动 Redis
sudo service redis-server start  # Linux
brew services start redis        # macOS

# 测试连接
redis-cli ping  # 应该返回 PONG
```

### 4. 安装 Python 依赖

```bash
cd backend

# 方式 1: 使用虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### 5. 配置环境变量

```bash
# 复制环境变量模板
cp ../.env.local .env

# 编辑 .env 文件，设置你的 API Keys
nano .env
```

**必需配置:**
```bash
# OpenAI API Key
OPENAI_API_KEY=sk-your-key-here

# 或使用国内服务（如 SiliconFlow）
OPENAI_BASE_URL=https://api.siliconflow.cn/v1
OPENAI_API_KEY=sk-your-siliconflow-key

# 搜索引擎
RETRIEVER=ddg  # DuckDuckGo 免费无需 key
```

### 6. 初始化数据库

```bash
# 确保虚拟环境已激活
source venv/bin/activate

# 运行初始化脚本
python scripts/init_db.py
```

### 7. 启动开发服务器

```bash
# 方式 1: 使用启动脚本
python scripts/dev.py

# 方式 2: 直接使用 uvicorn
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

访问：
- API 文档: http://127.0.0.1:8000/api/v1/docs
- 健康检查: http://127.0.0.1:8000/health

---

## 方案二：简化环境（SQLite）

如果不想安装 PostgreSQL 和 Redis，可以使用 SQLite。

### 1. 修改 `.env` 文件

```bash
# 注释掉 PostgreSQL，使用 SQLite
# DATABASE_URL=postgresql://...

DATABASE_URL=sqlite:///./gpt_researcher.db

# 注释掉 Redis 相关配置
# REDIS_URL=redis://localhost:6379/0
# CELERY_BROKER_URL=redis://localhost:6379/1
```

### 2. 安装依赖

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. 初始化数据库

```bash
python scripts/init_db.py
```

### 4. 启动服务器

```bash
python scripts/dev.py
```

---

## 测试 API

### 1. 健康检查

```bash
curl http://127.0.0.1:8000/health
```

### 2. 创建研究任务

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/research" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "2025年人工智能最新发展",
    "report_type": "deep",
    "language": "chinese"
  }'
```

### 3. 查询研究状态

```bash
curl http://127.0.0.1:8000/api/v1/research/1
```

### 4. WebSocket 连接（实时进度）

使用 Python 测试：

```python
import asyncio
import websockets

async def test_websocket():
    uri = "ws://127.0.0.1:8000/api/v1/research/ws/1"

    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            print(f"收到: {message}")

asyncio.run(test_websocket())
```

---

## 开发工具

### 数据库管理

```bash
# 查看数据库
sqlite3 gpt_researcher.db  # SQLite
psql gpt_researcher        # PostgreSQL

# 查看表
.tables                    # SQLite
\dt                        # PostgreSQL
```

### 日志调试

```bash
# 启用详细日志
export DEBUG=True
python scripts/dev.py
```

### API 测试

使用 Swagger UI: http://127.0.0.1:8000/api/v1/docs

---

## 常见问题

### Q: ImportError: No module named 'xxx'

```bash
# 确保虚拟环境已激活
source venv/bin/activate

# 重新安装依赖
pip install -r requirements.txt
```

### Q: 数据库连接失败

```bash
# 检查 PostgreSQL 是否运行
sudo service postgresql status

# 检查数据库是否存在
psql -l
```

### Q: API Key 无效

确保 `.env` 文件中的 API Key 正确：

```bash
OPENAI_API_KEY=sk-...
```

### Q: 端口被占用

修改 `.env` 中的端口：

```bash
PORT=8001
```

---

## 生产部署

生产环境建议使用：
- Nginx 反向代理
- Gunicorn + Uvicorn workers
- PostgreSQL 持久化存储
- Redis 缓存
- Celery 异步任务

参考部署指南：
```bash
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

---

## 目录结构

```
backend/
├── app/
│   ├── api/v1/endpoints/    # API 路由
│   ├── core/                # 核心功能
│   ├── models/              # 数据模型
│   ├── tasks/               # 异步任务
│   └── main.py              # 应用入口
├── scripts/
│   ├── init_db.py          # 数据库初始化
│   ├── dev.py              # 开发服务器
│   └── install.sh          # 安装脚本
├── requirements.txt
├── .env                    # 环境配置
└── venv/                   # 虚拟环境
```

---

## 下一步

1. 配置你的 LLM API Key（OpenAI、SiliconFlow 等）
2. 启动服务器
3. 访问 http://127.0.0.1:8000/api/v1/docs 测试 API
4. 查看 `docs/` 了解完整功能设计
