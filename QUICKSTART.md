# 快速启动指南

## 🚀 5 分钟快速开始

### 最简单的方式（使用 SQLite）

```bash
# 1. 进入后端目录
cd backend

# 2. 创建虚拟环境并安装依赖
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. 配置环境变量
cp ../.env.local .env
# 编辑 .env，至少设置 OPENAI_API_KEY
nano .env

# 4. 初始化数据库
python scripts/init_db.py

# 5. 启动服务器
python scripts/dev.py
```

访问 http://127.0.0.1:8000/api/v1/docs 开始使用！

---

## 📋 最小配置要求

在 `.env` 文件中，**必须**配置：

```bash
# LLM API Key（三选一）
OPENAI_API_KEY=sk-xxx                    # OpenAI
# 或使用 SiliconFlow 等兼容服务
OPENAI_BASE_URL=https://api.siliconflow.cn/v1
OPENAI_API_KEY=sk-xxx

# 搜索引擎（推荐 DuckDuckGo，免费无需 key）
RETRIEVER=ddg
```

---

## 📚 详细文档

- **完整本地开发指南**: [backend/LOCAL_SETUP.md](backend/LOCAL_SETUP.md)
- **后端架构设计**: [docs/backend-design.md](docs/backend-design.md)
- **前端设计**: [docs/GPT-Researcher前端UX设计方案.md](docs/GPT-Researcher前端UX设计方案.md)

---

## 🧪 测试 API

```bash
# 健康检查
curl http://127.0.0.1:8000/health

# 创建研究任务
curl -X POST "http://127.0.0.1:8000/api/v1/research" \
  -H "Content-Type: application/json" \
  -d '{"query": "人工智能最新发展", "report_type": "deep"}'
```

---

## 🐳 Docker 方式

如果已安装 Docker：

```bash
docker-compose up -d
```

---

## ❓ 常见问题

**Q: 数据库连接失败？**
- 使用 SQLite 方式，修改 `.env` 中的 `DATABASE_URL=sqlite:///./gpt_researcher.db`

**Q: API Key 无效？**
- 检查 `.env` 中的 `OPENAI_API_KEY` 是否正确
- 如果使用国内服务，同时设置 `OPENAI_BASE_URL`

**Q: 端口被占用？**
- 修改 `.env` 中的 `PORT=8001`

---

## 📂 项目结构

```
my-researcher/
├── backend/           # 后端代码
│   ├── app/          # 应用代码
│   ├── scripts/      # 工具脚本
│   └── LOCAL_SETUP.md # 本地开发详细指南
├── docs/             # 设计文档
├── reference/        # 参考代码
└── .env.local        # 环境变量模板
```
