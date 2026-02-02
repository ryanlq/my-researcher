# GPT-Researcher 后端架构设计方案

基于 gpt-researcher 框架的完整后端系统设计

---

## 一、架构概述

### 1.1 技术栈

```yaml
核心框架:
  框架: FastAPI 0.104+
  Python: 3.10+
  异步: asyncio + aiohttp

数据库:
  主数据库: PostgreSQL 15+
  向量库: PGVector / Qdrant / Weaviate
  缓存: Redis 7+

任务队列:
  队列: Celery + Redis
  调度: Celery Beat

实时通信:
  WebSocket: FastAPI WebSocket
  消息队列: Redis Pub/Sub

文件存储:
  本地存储: /data/uploads
  云存储: S3 / OSS (可选)

监控:
  日志: Python logging + ELK
  指标: Prometheus + Grafana
  追踪: OpenTelemetry

认证:
  认证: JWT
  权限: RBAC
```

### 1.2 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                         客户端                              │
│                    (NextJS / React / CLI)                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ HTTP / WebSocket
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                     API Gateway                               │
│                   (Nginx / Traefik)                             │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┬─────────────┐
        │             │             │             │
┌───────▼────┐  ┌────▼──────┐  ┌───▼────────┐  ┌───▼────────┐
│   FastAPI   │  │  WebSocket│  │  Celery     │  │  PostgreSQL │
│   Service   │  │  Server   │  │  Worker     │  │  Database   │
│             │  │           │  │             │  │             │
│ 研究接口     │  │ 进度推送   │  │ 异步任务     │  │  数据存储   │
│ 任务管理     │  │           │  │             │  │  用户数据   │
│ 报告生成     │  │           │  │ 深度研究     │  │  研究历史   │
└───────┬────┘  └─────┬─────┘  └──────┬──────┘  └─────────────┘
        │             │                │
        └─────────────┼────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                  GPT-Researcher Core                         │
│  (pip 包: gpt-researcher + skills + retrievers)           │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、项目结构

### 2.1 目录结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 应用入口
│   │
│   ├── api/                    # API 路由
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── research.py      # 研究相关接口
│   │   │   ├── knowledge.py      # 知识库接口
│   │   │   ├── config.py         # 配置接口
│   │   │   ├── websocket.py      # WebSocket 接口
│   │   │   └── health.py         # 健康检查
│   │   └── deps.py               # 依赖注入
│   │
│   ├── core/                   # 核心业务逻辑
│   │   ├── __init__.py
│   │   ├── research/
│   │   │   ├── __init__.py
│   │   │   ├── coordinator.py   # 研究协调器
│   │   │   ├── executor.py       # 研究执行器
│   │   │   ├── deep_research.py  # 深度研究
│   │   │   └── multi_agent.py    # 多代理协作
│   │   │
│   │   ├── report/
│   │   │   ├── __init__.py
│   │   │   ├── generator.py      # 报告生成器
│   │   │   └── exporter.py       # 多格式导出
│   │   │
│   │   ├── knowledge/
│   │   │   ├── __init__.py
│   │   │   ├── document.py       # 文档管理
│   │   │   ├── vector_store.py   # 向量存储
│   │   │   └── retriever.py      # 检索器
│   │   │
│   │   └── llm/
│   │       ├── __init__.py
│   │       ├── provider.py       # LLM 提供商管理
│   │       └── cost_tracker.py   # 成本追踪
│   │
│   ├── models/                 # 数据模型
│   │   ├── __init__.py
│   │   ├── research.py          # 研究任务模型
│   │   ├── user.py              # 用户模型
│   │   ├── document.py          # 文档模型
│   │   └── config.py            # 配置模型
│   │
│   ├── schemas/                # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── research.py
│   │   ├── websocket.py
│   │   └── config.py
│   │
│   ├── services/               # 外部服务
│   │   ├── __init__.py
│   │   ├── websocket.py         # WebSocket 服务
│   │   ├── task_queue.py        # 任务队列
│   │   └── storage.py           # 文件存储
│   │
│   ├── db/                     # 数据库
│   │   ├── __init__.py
│   │   ├── session.py           # 数据库会话
│   │   ├── base.py              # Base 类
│   │   └── repositories.py       # Repository
│   │
│   ├── utils/                  # 工具函数
│   │   ├── __init__.py
│   │   ├── config.py            # 配置管理
│   │   ├── logger.py            # 日志工具
│   │   └── helpers.py           # 辅助函数
│   │
│   └── middleware/             # 中间件
│       ├── __init__.py
│       ├── auth.py              # 认证中间件
│       ├── cors.py              # CORS 中间件
│       └── rate_limit.py        # 速率限制
│
├── workers/                    # Celery workers
│   ├── __init__.py
│   ├── research_worker.py     # 研究任务 worker
│   └── export_worker.py        # 导出任务 worker
│
├── tests/                      # 测试
│   ├── __init__.py
│   ├── test_api/
│   ├── test_core/
│   └── conftest.py
│
├── scripts/                    # 脚本
│   ├── init_db.py              # 初始化数据库
│   └── migrate.py              # 数据迁移
│
├── .env.example                # 环境变量示例
├── pyproject.toml              # Python 依赖
├── Dockerfile                  # Docker 配置
└── docker-compose.yml          # Docker Compose 配置
```

---

## 三、核心 API 设计

### 3.1 研究接口

```python
# app/api/v1/research.py

from fastapi import APIRouter, BackgroundTasks, Depends
from app.schemas.research import (
    ResearchCreateRequest,
    ResearchResponse,
    ResearchProgressResponse
)
from app.core.research.executor import ResearchExecutor
from app.services.websocket import WebSocketManager

router = APIRouter(prefix="/api/v1/research", tags=["研究"])

@router.post("/start", response_model=ResearchResponse)
async def start_research(
    request: ResearchCreateRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    ws_manager: WebSocketManager = Depends()
) -> ResearchResponse:
    """
    启动研究任务

    支持的模式:
    - standard: 标准研究 (1-2分钟)
    - deep: 深度研究 (5-10分钟)
    - multi_agent: 多代理协作 (10-20分钟)
    - knowledge: 知识库研究
    """

    # 创建研究任务
    research = Research(
        query=request.query,
        report_type=request.report_type,
        user_id=current_user.id,
        config=request.config
    )

    # 保存到数据库
    await research.save()

    # 异步执行研究
    background_tasks.add_task(
        execute_research,
        research_id=research.id,
        ws_manager=ws_manager
    )

    return ResearchResponse(
        research_id=research.id,
        status="started",
        estimated_time=research.estimate_duration(),
        estimated_cost=research.estimate_cost()
    )


@router.get("/{research_id}/progress", response_model=ResearchProgressResponse)
async def get_research_progress(
    research_id: str,
    current_user: User = Depends(get_current_user)
) -> ResearchProgressResponse:
    """获取研究进度"""
    research = await Research.get(research_id, user_id=current_user.id)

    return ResearchProgressResponse(
        research_id=research.id,
        status=research.status,
        progress=research.progress,
        current_stage=research.current_stage,
        completed_queries=research.completed_queries,
        total_queries=research.total_queries,
        current_cost=research.current_cost,
        estimated_cost=research.estimated_cost,
        started_at=research.created_at,
        updated_at=research.updated_at
    )


@router.post("/{research_id}/cancel")
async def cancel_research(
    research_id: str,
    current_user: User = Depends(get_current_user)
):
    """取消研究任务"""
    research = await Research.get(research_id, user_id=current_user.id)

    if research.status != "running":
        raise HTTPException(400, "只能取消运行中的研究")

    await research.cancel()

    return {"message": "研究已取消", "research_id": research_id}


@router.get("/{research_id}/result")
async def get_research_result(
    research_id: str,
    current_user: User = Depends(get_current_user)
):
    """获取研究结果"""
    research = await Research.get(research_id, user_id=current_user.id)

    if research.status != "completed":
        raise HTTPException(400, "研究尚未完成")

    return {
        "research_id": research.id,
        "query": research.query,
        "report": research.report,
        "sources": research.sources,
        "cost": research.total_cost,
        "duration": research.duration,
        "created_at": research.created_at,
        "completed_at": research.completed_at
    }


@router.get("/{research_id}/export/{format}")
async def export_report(
    research_id: str,
    format: str,  # pdf, docx, markdown
    current_user: User = Depends(get_current_user)
):
    """导出报告"""
    research = await Research.get(research_id, user_id=current_user.id)

    if research.status != "completed":
        raise HTTPException(400, "研究尚未完成")

    exporter = ReportExporter()

    if format == "pdf":
        file_path = await export_to_pdf(research, exporter)
    elif format == "docx":
        file_path = await export_to_docx(research, exporter)
    elif format == "markdown":
        file_path = await export_to_markdown(research, exporter)
    else:
        raise HTTPException(400, "不支持的格式")

    return FileResponse(
        path=file_path,
        media_type="application/octet-stream",
        filename=f"research_{research.id}.{format}"
    )
```

### 3.2 WebSocket 接口

```python
# app/api/v1/websocket.py

from fastapi import WebSocket, WebSocketDisconnect
from app.services.websocket import WebSocketManager

ws_manager = WebSocketManager()

@router.websocket("/ws/research/{research_id}")
async def research_websocket(
    websocket: WebSocket,
    research_id: str,
    token: str
):
    """
    WebSocket 连接用于实时推送研究进度

    事件类型:
    - research.started: 研究开始
    - research.progress: 进度更新
    - research.stage: 阶段变更
    - research.completed: 研究完成
    - research.error: 研究错误
    - research.cancelled: 研究取消
    """

    # 验证 token 和研究权限
    user = await verify_ws_token(token)
    research = await Research.get(research_id, user_id=user.id)

    if not research:
        await websocket.close(code=1008)
        return

    await ws_manager.connect(research_id, websocket)

    try:
        # 发送初始状态
        await websocket.send_json({
            "type": "research.connected",
            "research_id": research_id,
            "status": research.status,
            "progress": research.progress
        })

        # 监听客户端消息（暂停/继续/取消）
        while True:
            data = await websocket.receive_json()

            if data.get("action") == "pause":
                await research.pause()
                await ws_manager.broadcast(research_id, {
                    "type": "research.paused",
                    "research_id": research_id
                })
            elif data.get("action") == "resume":
                await research.resume()
                await ws_manager.broadcast(research_id, {
                    "type": "research.resumed",
                    "research_id": research_id
                })
            elif data.get("action") == "cancel":
                await research.cancel()
                await ws_manager.broadcast(research_id, {
                    "type": "research.cancelled",
                    "research_id": research_id
                })
                break

    except WebSocketDisconnect:
        await ws_manager.disconnect(research_id, websocket)
```

### 3.3 知识库接口

```python
# app/api/v1/knowledge.py

from fastapi import APIRouter, UploadFile, File
from app.core.knowledge.document import DocumentManager
from app.core.knowledge.vector_store import VectorStoreManager

router = APIRouter(prefix="/api/v1/knowledge", tags=["知识库"])

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    doc_manager: DocumentManager = Depends()
):
    """
    上传文档到知识库

    支持的格式: PDF, DOCX, PPTX, XLSX, TXT, MD
    """

    # 验证文件类型和大小
    if file.size > 50 * 1024 * 1024:  # 50MB
        raise HTTPException(400, "文件大小不能超过 50MB")

    # 保存文件
    file_path = await doc_manager.save_file(file, user.id)

    # 提取文本
    text_content = await doc_manager.extract_text(file_path)

    # 创建 LangChain Documents
    documents = await doc_manager.create_documents(
        text=text_content,
        metadata={
            "source": file.filename,
            "user_id": user.id,
            "file_path": file_path
        }
    )

    # 存入向量库
    vector_store = VectorStoreManager()
    await vector_store.add_documents(documents)

    return {
        "document_id": documents[0].metadata["id"],
        "filename": file.filename,
        "status": "processed",
        "chunks": len(documents)
    }


@router.get("/documents")
async def list_documents(
    user: User = Depends(get_current_user),
    doc_manager: DocumentManager = Depends()
):
    """列出用户的所有文档"""
    documents = await doc_manager.list_documents(user.id)

    return {
        "total": len(documents),
        "documents": [
            {
                "id": doc.id,
                "filename": doc.filename,
                "file_type": doc.file_type,
                "size": doc.size,
                "uploaded_at": doc.uploaded_at,
                "status": doc.status
            }
            for doc in documents
        ]
    }


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    user: User = Depends(get_current_user),
    doc_manager: DocumentManager = Depends(),
    vector_store: VectorStoreManager = Depends()
):
    """删除文档"""
    # 从数据库删除
    await doc_manager.delete_document(document_id, user.id)

    # 从向量库删除
    await vector_store.delete_documents(document_id)

    return {"message": "文档已删除"}
```

### 3.4 配置接口

```python
# app/api/v1/config.py

from fastapi import APIRouter, Depends
from app.schemas.config import ConfigUpdate, ConfigResponse

router = APIRouter(prefix="/api/v1/config", tags=["配置"])

@router.get("/", response_model=ConfigResponse)
async def get_config(
    user: User = Depends(get_current_user)
):
    """获取用户配置"""
    return ConfigResponse(
        llm_providers=user.config.llm_providers,
        retrievers=user.config.retrievers,
        research_params=user.config.research_params
    )


@router.put("/", response_model=ConfigResponse)
async def update_config(
    config_update: ConfigUpdate,
    user: User = Depends(get_current_user)
):
    """更新用户配置"""
    await user.update_config(config_update)

    return ConfigResponse(
        llm_providers=user.config.llm_providers,
        retrievers=user.config.retrievers,
        research_params=user.config.research_params
    )


@router.post("/test-connection")
async def test_llm_connection(
    provider: str,
    user: User = Depends(get_current_user)
):
    """测试 LLM 连接"""
    tester = LLMConnectionTester()

    is_connected, error = await tester.test(provider, user.config)

    return {
        "provider": provider,
        "status": "connected" if is_connected else "failed",
        "error": error
    }
```

---

## 四、核心业务逻辑

### 4.1 研究执行器

```python
# app/core/research/executor.py

import asyncio
from typing import Optional
from gpt_researcher import GPTResearcher
from app.models.research import Research
from app.services.websocket import WebSocketManager

class ResearchExecutor:
    """研究执行器"""

    def __init__(self):
        self.ws_manager = WebSocketManager()

    async def execute_research(
        self,
        research_id: str,
        ws_manager: WebSocketManager
    ):
        """
        执行研究任务

        Args:
            research_id: 研究 ID
            ws_manager: WebSocket 管理器
        """
        research = await Research.get(research_id)

        try:
            # 更新状态为运行中
            await research.update_status("running")
            await self._notify_start(research_id)

            # 创建 GPTResearcher 实例
            gpt_researcher = GPTResearcher(
                query=research.query,
                report_type=research.report_type,
                report_format=research.config.get("format", "markdown"),
                tone=research.config.get("tone", "Objective"),
                source_urls=research.config.get("source_urls"),
                mcp_configs=research.config.get("mcp_configs"),
                mcp_strategy=research.config.get("mcp_strategy", "fast"),
                max_subtopics=research.config.get("max_subtopics", 5),
                verbose=True,
                websocket=None  # 我们使用自定义 WebSocket
            )

            # 设置进度回调
            gpt_researcher.log_handler = self._create_log_handler(
                research_id, ws_manager
            )

            # 执行研究
            if research.report_type == "deep":
                context = await self._execute_deep_research(
                    gpt_researcher, research, ws_manager
                )
            elif research.report_type == "multi_agent":
                context = await self._execute_multi_agent_research(
                    gpt_researcher, research, ws_manager
                )
            else:
                context = await gpt_researcher.conduct_research()

            # 保存上下文
            await research.save_context(context)

            # 生成报告
            await self._notify_stage(research_id, "生成报告")
            report = await gpt_researcher.write_report(
                custom_prompt=research.config.get("custom_prompt")
            )

            # 获取统计信息
            costs = gpt_researcher.get_costs()
            sources = gpt_researcher.get_research_sources()

            # 保存结果
            await research.save_result(
                report=report,
                sources=sources,
                costs=costs
            )

            # 通知完成
            await self._notify_complete(research_id, {
                "report": report,
                "sources_count": len(sources),
                "costs": costs
            })

        except Exception as e:
            await research.update_status("failed")
            await self._notify_error(research_id, str(e))
            raise

    async def _execute_deep_research(
        self,
        gpt_researcher: GPTResearcher,
        research: Research,
        ws_manager: WebSocketManager
    ):
        """执行深度研究"""
        # 深度研究使用 DeepResearchSkill
        from app.core.research.deep_research import DeepResearchOrchestrator

        orchestrator = DeepResearchOrchestrator(
            gpt_researcher=gpt_researcher,
            research_id=research.id,
            ws_manager=ws_manager
        )

        # 执行深度研究
        context = await orchestrator.run(
            breadth=research.config.get("breadth", 5),
            depth=research.config.get("depth", 3),
            concurrency=research.config.get("concurrency", 4),
            on_progress=lambda p: self._on_deep_progress(
                research.id, p, ws_manager
            )
        )

        return context

    async def _execute_multi_agent_research(
        self,
        gpt_researcher: GPTResearcher,
        research: Research,
        ws_manager: WebSocketManager
    ):
        """执行多代理研究"""
        from app.core.research.multi_agent import MultiAgentOrchestrator

        orchestrator = MultiAgentOrchestrator(
            gpt_researcher=gpt_researcher,
            research_id=research.id,
            ws_manager=ws_manager
        )

        # 执行多代理研究
        report = await orchestrator.run(
            max_sections=research.config.get("max_sections", 5),
            follow_guidelines=research.config.get("follow_guidelines", False),
            guidelines=research.config.get("guidelines", []),
            include_human_feedback=research.config.get("human_feedback", False)
        )

        return report

    def _create_log_handler(self, research_id: str, ws_manager: WebSocketManager):
        """创建日志处理器"""
        async def log_handler(event_type: str, data: dict):
            await ws_manager.broadcast(research_id, {
                "type": f"research.{event_type}",
                "research_id": research_id,
                "data": data
            })

        return log_handler

    async def _notify_start(self, research_id: str):
        await self.ws_manager.broadcast(research_id, {
            "type": "research.started",
            "research_id": research_id,
            "timestamp": datetime.utcnow().isoformat()
        })

    async def _notify_progress(self, research_id: str, progress: dict):
        await self.ws_manager.broadcast(research_id, {
            "type": "research.progress",
            "research_id": research_id,
            "progress": progress
        })

    async def _notify_stage(self, research_id: str, stage: str):
        await self.ws_manager.broadcast(research_id, {
            "type": "research.stage",
            "research_id": research_id,
            "stage": stage
        })

    async def _notify_complete(self, research_id: str, result: dict):
        await self.ws_manager.broadcast(research_id, {
            "type": "research.completed",
            "research_id": research_id,
            "result": result
        })

    async def _notify_error(self, research_id: str, error: str):
        await self.ws_manager.broadcast(research_id, {
            "type": "research.error",
            "research_id": research_id,
            "error": error
        })
```

### 4.2 WebSocket 管理器

```python
# app/services/websocket.py

from fastapi import WebSocket
from typing import Dict, Set
import json

class WebSocketManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        # research_id -> WebSocket 连接的映射
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, research_id: str, websocket: WebSocket):
        """建立连接"""
        if research_id not in self.active_connections:
            self.active_connections[research_id] = set()

        self.active_connections[research_id].add(websocket)
        print(f"WebSocket connected: research_id={research_id}, "
              f"total_connections={len(self.active_connections[research_id])}")

    async def disconnect(self, research_id: str, websocket: WebSocket):
        """断开连接"""
        if research_id in self.active_connections:
            self.active_connections[research_id].discard(websocket)

            if not self.active_connections[research_id]:
                del self.active_connections[research_id]

        print(f"WebSocket disconnected: research_id={research_id}")

    async def broadcast(self, research_id: str, message: dict):
        """向研究任务的所有连接广播消息"""
        if research_id not in self.active_connections:
            return

        disconnected = set()

        for connection in self.active_connections[research_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error broadcasting to {research_id}: {e}")
                disconnected.add(connection)

        # 移除断开的连接
        for connection in disconnected:
            await self.disconnect(research_id, connection)

    async def send_personal(self, research_id: str, websocket: WebSocket, message: dict):
        """向特定连接发送消息"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"Error sending personal message: {e}")
            await self.disconnect(research_id, websocket)
```

### 4.3 深度研究协调器

```python
# app/core/research/deep_research.py

from gpt_researcher.skills.deep_research import DeepResearchSkill
from app.models.research import ResearchProgress

class DeepResearchOrchestrator:
    """深度研究协调器"""

    def __init__(
        self,
        gpt_researcher: GPTResearcher,
        research_id: str,
        ws_manager: WebSocketManager
    ):
        self.gpt_researcher = gpt_researcher
        self.research_id = research_id
        self.ws_manager = ws_manager
        self.progress = ResearchProgress(research_id=research_id)

    async def run(
        self,
        breadth: int = 5,
        depth: int = 3,
        concurrency: int = 4,
        on_progress = None
    ):
        """运行深度研究"""

        # 初始化进度追踪
        self.progress.initialize(
            total_depth=depth,
            total_breadth=breadth
        )

        await self._notify_progress()

        # 创建深度研究技能
        deep_research = DeepResearchSkill(self.gpt_researcher)

        # 自定义进度回调
        async def progress_callback(progress):
            self.progress.update(progress)
            await self._notify_progress()

            if on_progress:
                await on_progress(progress)

        # 执行深度研究
        context = await deep_research.run(
            on_progress=progress_callback
        )

        return context

    async def _notify_progress(self):
        """通知进度更新"""
        await self.ws_manager.broadcast(self.research_id, {
            "type": "deep_research.progress",
            "research_id": self.research_id,
            "progress": {
                "current_depth": self.progress.current_depth,
                "total_depth": self.progress.total_depth,
                "current_breadth": self.progress.current_breadth,
                "total_breadth": self.progress.total_breadth,
                "completed_queries": self.progress.completed_queries,
                "total_queries": self.progress.total_queries,
                "current_query": self.progress.current_query
            }
        })
```

---

## 五、数据模型

### 5.1 研究模型

```python
# app/models/research.py

from sqlalchemy import Column, String, DateTime, JSON, Float, Integer
from sqlalchemy.ext.asyncio import AsyncAttrs
from app.db.base import Base

class Research(Base, AsyncAttrs):
    """研究任务模型"""

    __tablename__ = "researches"

    # 主键
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # 用户关联
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

    # 查询信息
    query = Column(String, nullable=False)
    report_type = Column(String, nullable=False, default="research_report")
    report_format = Column(String, default="markdown")

    # 配置
    config = Column(JSON, nullable=False, default=dict)

    # 状态
    status = Column(String, nullable=False, default="pending")  # pending, running, paused, completed, failed, cancelled

    # 进度
    progress = Column(JSON, default=dict)
    current_stage = Column(String)

    # 统计
    completed_queries = Column(Integer, default=0)
    total_queries = Column(Integer, default=0)
    current_cost = Column(Float, default=0.0)
    estimated_cost = Column(Float)
    total_cost = Column(Float)

    # 结果
    context = Column(Text)
    report = Column(Text)
    sources = Column(JSON)

    # 时间
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)

    # 用户关系
    user = relationship("User", back_populates="researches")

    async def save(self):
        """保存到数据库"""
        async with get_db() as db:
            db.add(self)
            await db.commit()
            await db.refresh(self)

    async def update_status(self, status: str):
        """更新状态"""
        self.status = status
        self.updated_at = datetime.utcnow()

        if status == "running" and not self.started_at:
            self.started_at = datetime.utcnow()
        elif status == "completed":
            self.completed_at = datetime.utcnow()

        await self.save()

    async def save_context(self, context: str):
        """保存研究上下文"""
        self.context = context
        await self.save()

    async def save_result(self, report: str, sources: list, costs: float):
        """保存研究结果"""
        self.report = report
        self.sources = sources
        self.total_cost = costs
        self.status = "completed"
        await self.save()

    async def cancel(self):
        """取消研究"""
        self.status = "cancelled"
        await self.save()

    def estimate_duration(self) -> int:
        """估算耗时（秒）"""
        if self.report_type == "deep":
            return 300  # 5 分钟
        elif self.report_type == "multi_agent":
            return 600  # 10 分钟
        else:
            return 60   # 1 分钟

    def estimate_cost(self) -> float:
        """估算成本"""
        if self.report_type == "deep":
            return 0.40
        elif self.report_type == "multi_agent":
            return 0.50
        else:
            return 0.05
```

### 5.2 用户模型

```python
# app/models/user.py

from sqlalchemy import Column, String, Boolean, DateTime, JSON
from sqlalchemy.ext.asyncio import AsyncAttrs
from app.db.base import Base

class User(Base, AsyncAttrs):
    """用户模型"""

    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)

    # 配置
    config = Column(JSON, nullable=False, default=lambda: {
        "llm_providers": {
            "fast": {"provider": "ollama", "model": "llama3.2"},
            "smart": {"provider": "openai", "model": "gpt-4o"},
            "strategic": {"provider": "openai", "model": "o4-mini"},
            "embedding": {"provider": "ollama", "model": "nomic-embed"}
        },
        "retrievers": {
            "default": "mcp",
            "mcp_servers": [...]
        },
        "research_params": {
            "depth": {"breadth": 5, "depth": 3, "concurrency": 4}
        },
        "api_keys": {...}
    })

    # 计费
    credits = Column(Float, default=10.0)  # 赠送积分
    monthly_usage = Column(Float, default=0.0)

    # 时间
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

    # 关系
    researches = relationship("Research", back_populates="user")
    documents = relationship("Document", back_populates="user")

    async def update_config(self, config_update: dict):
        """更新配置"""
        self.config = {**self.config, **config_update}
        await self.save()
```

---

## 六、WebSocket 通信协议

### 6.1 客户端 → 服务端

```typescript
// 启动研究
{
  "action": "start",
  "query": "2025年AI在教育领域的应用"
}

// 暂停研究
{
  "action": "pause",
  "research_id": "uuid"
}

// 继续研究
{
  "action": "resume",
  "research_id": "uuid"
}

// 取消研究
{
  "action": "cancel",
  "research_id": "uuid"
}
```

### 6.2 服务端 → 客户端

```typescript
// 连接建立
{
  "type": "research.connected",
  "research_id": "uuid",
  "status": "running"
}

// 进度更新
{
  "type": "research.progress",
  "research_id": "uuid",
  "progress": {
    "current_depth": 2,
    "total_depth": 3,
    "completed_queries": 8,
    "total_queries": 15,
    "current_query": "AI在K-12教育中的应用"
  }
}

// 阶段变更
{
  "type": "research.stage",
  "research_id": "uuid",
  "stage": "生成报告"
}

// 研究完成
{
  "type": "research.completed",
  "research_id": "uuid",
  "result": {
    "report": "...",
    "sources": [...],
    "costs": 0.42
  }
}

// 错误
{
  "type": "research.error",
  "research_id": "uuid",
  "error": "API rate limit exceeded"
}
```

---

## 七、任务队列设计

### 7.1 Celery 任务定义

```python
# workers/research_worker.py

from celery import Celery
from app.core.research.executor import ResearchExecutor

celery_app = Celery(
    'gpt_researcher',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)

@celery_app.task(bind=True)
def execute_research_task(research_id: str):
    """
    异步执行研究任务

    Args:
        research_id: 研究 ID
    """
    import asyncio

    executor = ResearchExecutor()

    # 运行研究（同步包装）
    asyncio.run(_run_research(research_id, executor))

async def _run_research(research_id: str, executor: ResearchExecutor):
    """异步运行研究"""
    # 获取 WebSocket 管理器
    from app.services.websocket import get_ws_manager
    ws_manager = get_ws_manager()

    # 执行研究
    await executor.execute_research(research_id, ws_manager)


@celery_app.task
def export_report_task(research_id: str, format: str):
    """
    异步导出报告

    Args:
        research_id: 研究 ID
        format: 导出格式 (pdf, docx, markdown)
    """
    import asyncio

    asyncio.run(_run_export(research_id, format))

async def _run_export(research_id: str, format: str):
    """异步运行导出"""
    from app.core.report.exporter import ReportExporter

    exporter = ReportExporter()
    research = await Research.get(research_id)

    if format == "pdf":
        await export_to_pdf(research, exporter)
    elif format == "docx":
        await export_to_docx(research, exporter)
```

### 7.2 任务调度

```python
# workers/scheduler.py

from celery.schedules import crontab
from celery.decorators import periodic_task

@periodic_task(run_every=3600)  # 每小时
def cleanup_old_research():
    """清理过期的研究数据"""
    import asyncio
    from app.db.session import get_db
    from app.models.research import Research
    from datetime import datetime, timedelta

    async def _cleanup():
        async with get_db() as db:
            # 删除 7 天前的研究
            cutoff = datetime.utcnow() - timedelta(days=7)
            await Research.filter(
                Research.created_at < cutoff,
                Research.status == "completed"
            ).delete()
            await db.commit()

    asyncio.run(_cleanup())


@periodic_task(run_every=300)  # 每 5 分钟
def update_research_costs():
    """更新研究成本统计"""
    pass
```

---

## 八、数据库设计

### 8.1 数据表结构

```sql
-- 用户表
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    config JSONB NOT NULL DEFAULT '{}',
    credits DECIMAL(10, 2) DEFAULT 10.00,
    monthly_usage DECIMAL(10, 2) DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    INDEX idx_email (email)
);

-- 研究任务表
CREATE TABLE researches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    query TEXT NOT NULL,
    report_type VARCHAR(50) NOT NULL,
    report_format VARCHAR(20) DEFAULT 'markdown',
    config JSONB NOT NULL DEFAULT '{}',
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    progress JSONB DEFAULT '{}',
    current_stage VARCHAR(100),
    completed_queries INTEGER DEFAULT 0,
    total_queries INTEGER DEFAULT 0,
    current_cost DECIMAL(10, 6) DEFAULT 0.0,
    estimated_cost DECIMAL(10, 6),
    total_cost DECIMAL(10, 6),
    context TEXT,
    report TEXT,
    sources JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);

-- 文档表
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_type VARCHAR(50),
    file_size BIGINT,
    status VARCHAR(20) DEFAULT 'processing',
    chunk_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
);

-- API 密钥表
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    key_hash VARCHAR(255) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP WITH TIME ZONE,
    INDEX idx_user_id (user_id)
);
```

---

## 九、安全性设计

### 9.1 认证授权

```python
# app/middleware/auth.py

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """获取当前用户"""

    try:
        token = credentials.credentials
        payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = await User.get(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
```

### 9.2 速率限制

```python
# app/middleware/rate_limit.py

from slowapi import Limiter
from fastapi import Request

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/research/start")
@limiter.limit("10/hour")  # 每小时 10 次
async def start_research(
    request: Request,
    user: User = Depends(get_current_user)
):
    """限制研究频率"""
    pass
```

### 9.3 成本控制

```python
# app/core/llm/cost_tracker.py

class CostTracker:
    """成本追踪器"""

    def __init__(self):
        self.daily_limits = {
            "free": 5.0,      # 免费用户每天 $5
            "pro": 50.0,      # Pro 用户每天 $50
            "enterprise": 500.0  # 企业用户无限
        }

    async def check_budget(self, user: User, estimated_cost: float) -> bool:
        """检查预算是否充足"""
        daily_limit = self.daily_limits.get(user.plan, 5.0)
        today_usage = await self.get_today_usage(user.id)

        return (today_usage + estimated_cost) <= daily_limit

    async def track_cost(self, user: User, cost: float):
        """追踪成本"""
        user.monthly_usage += cost
        await user.save()
```

---

## 十、部署方案

### 10.1 Docker Compose 配置

```yaml
# docker-compose.yml

version: '3.8'

services:
  # FastAPI 后端
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/gpt_researcher
      - REDIS_URL=redis://redis:6379/0
      - JWT_SECRET=${JWT_SECRET}
    volumes:
      - ./data/uploads:/data/uploads
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  # Celery Worker
  worker:
    build: .
    command: celery -A workers.research_worker worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/gpt_researcher
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./data/uploads:/data/uploads
    depends_on:
      - postgres
      - redis
      - backend
    restart: unless-stopped

  # Celery Beat (定时任务)
  beat:
    build: .
    command: celery -A workers.beat beat --loglevel=info
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/gpt_researcher
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  # PostgreSQL
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=gpt_researcher
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  # Redis
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  # Nginx (API Gateway)
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### 10.2 生产环境建议

```yaml
架构: 负载均衡 + 多实例

组件:
  - Nginx: 负载均衡和 SSL 终止
  - FastAPI: 3-5 个实例（根据负载）
  - PostgreSQL: 主从复制
  - Redis: 哨群模式

扩展:
  - 水平扩展: 增加 FastAPI 实例
  - 垂直扩展: 升级数据库配置

监控:
  - Prometheus: 指标收集
  - Grafana: 可视化
  - Sentry: 错误追踪

部署:
  - Docker Swarm / Kubernetes
  - CI/CD: GitHub Actions / GitLab CI
```

---

## 十一、监控与日志

### 11.1 日志配置

```python
# app/utils/logger.py

import logging
import sys
from app.utils.config import settings

def setup_logging():
    """配置日志系统"""

    # 创建 logger
    logger = logging.getLogger("gpt_researcher")
    logger.setLevel(logging.INFO)

    # 控制台格式
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(
        logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    )

    # 文件输出（按天轮转）
    from logging.handlers import RotatingFileHandler

    file_handler = RotatingFileHandler(
        "logs/app.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=30
    )
    file_handler.setFormatter(
        logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
    )

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
```

### 11.2 性能监控

```python
# app/utils/metrics.py

from prometheus_client import Counter, Histogram, Gauge

# 定义指标
research_counter = Counter(
    "research_total",
    "Total number of research tasks",
    ["status", "report_type"]
)

research_duration = Histogram(
    "research_duration_seconds",
    "Research duration in seconds",
    ["report_type"]
)

research_cost = Histogram(
    "research_cost_dollars",
    "Research cost in dollars",
    ["report_type"]
)

active_researches = Gauge(
    "active_researches",
    "Number of active research tasks"
)

# 使用示例
@research_counter.labels(status="started", report_type="deep").inc()
@research_duration.labels(report_type="deep").observe(time)
```

---

## 十二、总结

### 核心特点

✅ **模块化架构** - 清晰的分层设计，易于维护
✅ **异步高性能** - FastAPI + asyncio + Celery
✅ **实时通信** - WebSocket 推送研究进度
✅ **可扩展** - 支持水平和垂直扩展
✅ **任务队列** - Celery 处理长时间任务
✅ **向量集成** - 完整的向量数据库支持
✅ **安全可靠** - JWT 认证 + 速率限制 + 成本控制

### 技术亮点

1. **双模式执行** - 同步（API）+ 异步（队列）
2. **进度实时推送** - WebSocket 全程追踪
3. **多研究模式** - 标准/深度/多代理/知识库
4. **LLM 灵活配置** - 支持本地+云端混合
5. **成本精确追踪** - 实时计算和预警

### 性能指标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| API 响应时间 | < 100ms | P95 |
| WebSocket 延迟 | < 50ms | 消息推送延迟 |
| 并发研究数 | 100+ | 同时运行的研究任务 |
| 数据库连接池 | 20 | 连接池大小 |
| 任务队列吞吐 | 50 tasks/min | Celery worker 数 |

---

后端架构设计已完成，包含完整的 API 设计、WebSocket 通信、任务队列、数据模型和部署方案。

需要我开始实现代码吗？我可以先从核心模块开始创建。
