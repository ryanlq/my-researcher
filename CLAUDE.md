# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GPT-Researcher is an AI-powered research automation platform built on the [gpt-researcher](https://github.com/assafelovic/gpt-researcher) framework. It provides comprehensive research capabilities with real-time WebSocket progress tracking and multi-modal outputs.

**Architecture**: Python FastAPI backend + Next.js 14 frontend (shadcn/ui)

**Core Technology**: Uses `gpt-researcher` Python package (v0.3.5) for all research execution, with MCP (Model Context Protocol) integration for extensible search sources.

## Essential Commands

### Backend Development (Local, No Docker)

```bash
cd backend

# Install dependencies (requires Python 3.10+)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Initialize database (SQLite default, PostgreSQL optional)
python scripts/init_db.py

# Start development server
python scripts/dev.py
# Server runs at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### Frontend Development

```bash
cd frontend

# Install dependencies
pnpm install  # or npm install

# Start dev server
pnpm dev      # or npm run dev
# Runs at http://localhost:3000
```

### Start All Services (One Command)

```bash
# From project root
./start.sh          # Start both backend and frontend
./start.sh stop     # Stop all services
./start.sh logs     # View logs
./start.sh status   # Check status
```

### Docker Compose (Full Stack)

```bash
docker-compose up -d     # Start all services (postgres, redis, backend, celery, qdrant)
docker-compose logs -f backend  # View backend logs
docker-compose down      # Stop all services
```

### Database Management

```bash
cd backend

# Initialize database (creates tables)
python scripts/init_db.py

# Force recreate database tables
python scripts/init_db.py --force

# Create default user
python scripts/create_default_user.py

# Verify pgvector extension (PostgreSQL only)
python scripts/verify_pgvector.py
```

### Testing

Currently no formal test suite exists in `backend/tests/`. The codebase relies on manual testing via the API documentation at `/docs`.

## Architecture

### Backend Structure

The backend has **two parallel implementations**:

1. **Simplified Implementation** (`backend/app/main.py`) - Direct use of `gpt-researcher` package with WebSocket support
2. **Structured Implementation** (`backend/app/api/v1/`) - Full-featured API with database, WebSocket manager, and Celery integration

**Key Modules:**

- `app/main.py` - Simplified FastAPI app (primary entry point for local dev)
- `app/core/config.py` - Centralized settings via pydantic-settings
- `app/core/research/executor.py` - ResearchExecutor class wrapping `gpt-researcher`
- `app/core/websocket/manager.py` - WebSocket connection management for real-time progress
- `app/api/v1/endpoints/research.py` - REST API endpoints
- `app/models/database.py` - SQLAlchemy models (User, Research, Document, etc.)
- `app/tasks/research_tasks.py` - Celery task definitions

### Research Execution Flow

```
1. Frontend sends research request → FastAPI endpoint
2. Create Research record in database (status: "pending")
3. Start background execution (thread or Celery task)
4. ResearchExecutor creates GPTResearcher instance with:
   - query, report_type, report_format, tone
   - Optional: websocket for streaming progress
   - Optional: mcp_configs for custom search sources
5. Execute: await researcher.conduct_research()
6. Generate report: await researcher.write_report()
7. Extract results: sources, costs, images
8. Update database (status: "completed")
9. WebSocket broadcasts final results to frontend
```

### Configuration System

All settings in `app/core/config.py` (Settings class). Environment variables from `.env`:

**Required:**
- `OPENAI_API_KEY` - LLM API key (or compatible like SiliconFlow)
- `DATABASE_URL` - Default: SQLite (`sqlite:///./gpt_researcher.db`)

**Important Optional:**
- `OPENAI_BASE_URL` - For OpenAI-compatible APIs (e.g., `https://api.siliconflow.cn/v1`)
- `RETRIEVER` - Search source: `tavily`, `ddg` (DuckDuckGo), `google`, `searxng`
- `FAST_LLM` / `SMART_LLM` - Model selection (format: `provider:model`)
- `DEEP_RESEARCH_BREADTH` / `DEPTH` / `CONCURRENCY` - Research parameters
- `CELERY_BROKER_URL` / `CELERY_RESULT_BACKEND` - Redis URLs for async tasks

### WebSocket Integration

The simplified `main.py` supports WebSocket at `/ws/research`:

```python
# GPTResearcher sends progress automatically when websocket is passed
researcher = GPTResearcher(
    query=query,
    report_type=report_type,
    websocket=websocket,  # Enables streaming
    verbose=True
)
await researcher.conduct_research()  # Progress events sent automatically
```

Events sent by gpt-researcher:
- `{"type": "logs", "content": "planning_research", "output": "..."}`
- `{"type": "logs", "content": "research_step_finalized", "output": "..."}`
- Final completion event with report, sources, costs, images

### Frontend Structure

- `src/app/page.tsx` - Main research interface
- `src/components/prompt/ResearchPromptInput.tsx` - Query input
- `src/components/sidebar/ResearchSidebar.tsx` - Research history
- `src/components/ui/` - shadcn/ui components
- `src/components/ResearchProgressPromptKit.tsx` - Real-time progress display

**State Management**: Zustand stores for research state, WebSocket connections

### MCP Integration

The project supports MCP (Model Context Protocol) for extending search sources:

- `reference/web_search_mcp.py` - Example SearXNG MCP server
- Configuration via `mcp_configs` parameter when creating GPTResearcher
- Set `MCP_STRATEGY=deep` in .env for multi-layer research with MCP

## Key Development Patterns

### Adding a New Research Type

1. Update `ResearchRequest` schema in `app/models/schemas.py`
2. Add logic in `ResearchExecutor.estimate_cost()` for cost/time estimation
3. Update GPTResearcher instantiation in `execute_research()` if needed

### Adding a New Retriever/Search Source

1. Configure via `RETRIEVER` environment variable (built-in options)
2. OR create custom MCP server in `reference/` and add to `mcp_configs`
3. Built-in retrievers: `tavily`, `google`, `duckduckgo`, `bing`, `searxng`

### WebSocket Customization

The simplified `main.py` passes websocket directly to GPTResearcher for automatic progress streaming. For custom progress handling, use the structured implementation with `WebSocketManager` class.

## Environment Setup

### Minimal `.env` (SQLite + DuckDuckGo)

```bash
OPENAI_API_KEY=sk-xxx
RETRIEVER=ddg
DATABASE_URL=sqlite:///./gpt_researcher.db
```

### Full Stack (PostgreSQL + Redis + Celery)

Use `docker-compose.yml` which includes:
- PostgreSQL 16 with pgvector extension
- Redis 7 (cache + Celery broker)
- Qdrant (vector database)
- Celery worker + Flower monitoring

## Important Notes

- The project includes both simplified and structured backend implementations
- Use `backend/app/main.py` for quick local development
- Use structured API (`backend/app/api/v1/`) for production features (auth, Celery, etc.)
- Frontend is in active development - check implementation status before adding features
- Research can take 2-20 minutes depending on type (standard, deep, multi-agent)
- All research progress is streamed via WebSocket for real-time UI updates
