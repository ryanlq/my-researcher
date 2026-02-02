"""
GPT Researcher - Simplified Backend
直接使用 gpt-researcher 官方包
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import json
import os
from dotenv import load_dotenv

# 加载 .env 文件 - 指定 backend 目录
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(backend_dir, '.env'))

# ✨ 设置 DOC_PATH 环境变量（gpt-researcher 需要）
import sys
from pathlib import Path
doc_path = Path(backend_dir) / 'data' / 'documents'
os.environ['DOC_PATH'] = str(doc_path)
print(f"📁 DOC_PATH 设置为: {os.environ['DOC_PATH']}")

from gpt_researcher import GPTResearcher

# CORS 配置 - 支持 JSON 格式和逗号分隔格式
def parse_cors_origins():
    cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000")
    try:
        # 尝试解析 JSON 格式
        import json
        return json.loads(cors_origins_str)
    except:
        # 否则用逗号分割
        return [origin.strip() for origin in cors_origins_str.split(",")]

CORS_ORIGINS = parse_cors_origins()

app = FastAPI(title="GPT Researcher API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========== 请求/响应模型 ==========

class ResearchRequest(BaseModel):
    query: str = Field(..., description="研究问题")
    report_type: str = Field(default="research_report", description="报告类型")
    report_format: str = Field(default="markdown", description="报告格式")
    tone: str = Field(default="objective", description="报告语气")
    language: str = Field(default="chinese", description="报告语言")


class ResearchResponse(BaseModel):
    report: str
    sources: List[str]
    costs: float
    images: List[str]


class CostEstimate(BaseModel):
    estimated_cost: float
    estimated_time_minutes: int
    estimated_queries: int


# ========== API 端点 ==========

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "GPT Researcher API",
        "version": "2.0 (Simplified)",
        "docs": "/docs"
    }


@app.post("/estimate", response_model=CostEstimate)
async def estimate_research(request: ResearchRequest):
    """
    估算研究成本和时间

    基于查询复杂度、报告类型和研究来源提供估算
    """
    # 基础估算逻辑
    base_cost = 0.15
    base_time = 2  # 分钟
    base_queries = 10

    # 根据报告类型调整
    if request.report_type == "deep":
        base_cost = 0.40
        base_time = 8
        base_queries = 75
    elif request.report_type == "multi_agent":
        base_cost = 0.80
        base_time = 20
        base_queries = 150

    # 根据研究来源调整成本
    # 指定URL研究成本更低，因为不需要额外的搜索
    if request.report_source == "static" and request.source_urls:
        if not request.complement_source_urls:
            # 仅研究指定URL，成本大幅降低
            base_cost *= 0.4
            base_time *= 0.6
            base_queries = len(request.source_urls) * 2
        else:
            # 指定URL + 全网补充，成本适中
            base_cost *= 0.7
            base_time *= 0.8

    # ✨ 本地文档研究 - 成本极低
    elif request.report_source == "local" and request.document_ids:
        # 仅处理本地文档，无搜索成本
        base_cost *= 0.2
        base_time *= 0.5
        base_queries = 0  # 无需查询

    # ✨ 混合研究 - URL + 本地文档
    elif request.report_source == "hybrid":
        if request.source_urls:
            # 有URL和文档，成本适中
            base_cost *= 0.5
            base_time *= 0.7
            base_queries = len(request.source_urls)
        else:
            # 仅文档，同local模式
            base_cost *= 0.2
            base_time *= 0.5
            base_queries = 0

    return CostEstimate(
        estimated_cost=round(base_cost, 2),
        estimated_time_minutes=int(base_time),
        estimated_queries=int(base_queries)
    )


@app.post("/research", response_model=ResearchResponse)
async def create_research(request: ResearchRequest):
    """
    创建并执行研究任务

    直接使用 gpt-researcher 官方包执行研究
    """
    try:
        # 构建 GPTResearcher 基础参数
        researcher_kwargs = {
            "query": request.query,
            "report_type": request.report_type,
            "report_format": request.report_format,
            "tone": request.tone,
        }

        # 处理指定来源研究
        if request.report_source and request.report_source != "web":
            # 指定URL研究（STATIC 或 HYBRID 模式）
            if request.source_urls:
                researcher_kwargs["source_urls"] = request.source_urls
                researcher_kwargs["complement_source_urls"] = request.complement_source_urls

            # ✨ 本地文档研究
            if request.report_source in ["local", "hybrid"] and request.document_ids:
                # 设置 report_source 参数
                researcher_kwargs["report_source"] = request.report_source

        # 创建 GPT Researcher 实例
        researcher = GPTResearcher(**researcher_kwargs)

        # 执行研究
        await researcher.conduct_research()

        # 生成报告
        report = await researcher.write_report()

        # 获取额外信息
        # 使用 get_research_sources() 而不是 get_source_urls()
        research_sources = researcher.get_research_sources()
        sources = [source.get("url") for source in research_sources if source.get("url")]
        costs = researcher.get_costs()
        images = researcher.get_research_images()

        return ResearchResponse(
            report=report,
            sources=sources or [],
            costs=costs or 0.0,
            images=images or []
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"研究执行失败: {str(e)}"
        )


@app.get("/research/{research_id}")
async def get_research(research_id: str):
    """
    获取研究结果（预留接口，当前不支持历史记录查询）
    """
    raise HTTPException(
        status_code=501,
        detail="历史记录查询功能未实现，请使用 /research 端点执行新研究"
    )


@app.get("/researches", response_model=List[dict])
async def list_researches():
    """
    列出研究历史（预留接口）
    """
    return []


# ========== WebSocket 端点 ==========

@app.websocket("/ws/research")
async def research_websocket(websocket: WebSocket):
    """
    WebSocket 端点用于实时研究进度更新（支持流式输出）

    连接到: ws://localhost:8000/ws/research

    客户端消息格式:
    {
        "query": "研究问题",
        "report_type": "research_report",
        "report_format": "markdown",
        "tone": "objective",
        "report_source": "web" | "static",
        "source_urls": ["url1", "url2"],
        "complement_source_urls": false
    }

    服务器推送事件（由 gpt-researcher 自动推送）:
    - {"type": "logs", "content": "planning_research", "output": "🌐 Browsing the web..."}
    - {"type": "logs", "content": "starting_research", "output": "🔍 Starting research..."}
    - {"type": "logs", "content": "research_step_finalized", "output": "✅ Completed..."}
    - {"type": "completed", "report": "...", "sources": [...]}
    """
    await websocket.accept()

    try:
        # 接收客户端请求
        data = await websocket.receive_json()

        query = data.get("query")
        report_type = data.get("report_type", "research_report")
        report_format = data.get("report_format", "markdown")
        tone = data.get("tone", "objective")
        report_source = data.get("report_source", "web")
        source_urls = data.get("source_urls")
        complement_source_urls = data.get("complement_source_urls", False)

        if not query:
            await websocket.send_json({
                "type": "error",
                "output": "Missing required field: query"
            })
            await websocket.close()
            return

        # 构建 researcher 参数
        researcher_kwargs = {
            "query": query,
            "report_type": report_type,
            "report_format": report_format,
            "tone": tone,
            "websocket": websocket,  # ⭐ 关键：传入 websocket 启用流式输出
            "verbose": True          # ⭐ 启用详细日志
        }

        # 处理指定来源研究
        if report_source and report_source != "web":
            # 指定URL研究
            if source_urls:
                researcher_kwargs["source_urls"] = source_urls
                researcher_kwargs["complement_source_urls"] = complement_source_urls

            # ✨ 本地文档研究
            document_ids = data.get("document_ids")
            if report_source in ["local", "hybrid"] and document_ids:
                researcher_kwargs["report_source"] = report_source

        # 创建 researcher 实例
        researcher = GPTResearcher(**researcher_kwargs)

        # 调试：显示实际使用的 retrievers
        print(f"🔧 DEBUG: Active retrievers: {[r.__name__ for r in researcher.retrievers]}")
        import os
        print(f"🔧 DEBUG: RETRIEVER env var: {os.getenv('RETRIEVER')}")
        print(f"🔧 DEBUG: Report source: {report_source}")
        print(f"🔧 DEBUG: Source URLs: {source_urls}")

        # 执行研究 - gpt-researcher 会自动通过 websocket 发送进度更新
        await researcher.conduct_research()

        # 生成报告
        report = await researcher.write_report()

        # 获取结果
        # 使用 get_research_sources() 而不是 get_source_urls()
        # 因为 visited_urls 可能为空，但 research_sources 包含实际的抓取数据
        research_sources = researcher.get_research_sources()
        sources = [source.get("url") for source in research_sources if source.get("url")]
        costs = researcher.get_costs()
        images = researcher.get_research_images()

        # 发送完成事件
        await websocket.send_json({
            "type": "completed",
            "output": "✅ 研究完成！",
            "report": report,
            "sources": sources or [],
            "costs": costs or 0.0,
            "images": images or []
        })

    except WebSocketDisconnect:
        print("WebSocket client disconnected")
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "output": f"❌ 研究失败: {str(e)}"
        })
    finally:
        try:
            await websocket.close()
        except:
            pass


# ========== 文档管理端点 ==========

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# 直接导入模块，避免触发 __init__.py
import importlib.util
spec = importlib.util.spec_from_file_location(
    "documents",
    Path(__file__).parent / "api" / "v1" / "endpoints" / "documents.py"
)
documents_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(documents_module)

app.include_router(documents_module.router, prefix="/documents", tags=["documents"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        # WebSocket 超时配置
        websocket_ping_interval=20,      # 每20秒发送一次心跳
        websocket_ping_timeout=60,       # 心跳超时60秒
        timeout_keep_alive=300,          # Keep-alive 超时5分钟
    )
