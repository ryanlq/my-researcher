# GPT-Researcher

AI-powered research automation platform with multi-modal research capabilities.

## Overview

GPT-Researcher is an advanced AI research tool that leverages the [gpt-researcher](https://github.com/assafelovic/gpt-researcher) framework to provide comprehensive, multi-layer research capabilities with real-time progress tracking and customizable outputs.

## Features

### Research Modes
- **Standard Research**: Quick single-layer research (1-2 minutes)
- **Deep Research**: Multi-layer exploration with 3 depth levels (5-10 minutes)
- **Multi-Agent**: LangGraph-based collaborative research (10-20 minutes)
- **Knowledge Base**: Hybrid research using local documents + web search

### Core Capabilities
- Real-time WebSocket progress updates
- Multiple LLM provider support (OpenAI, Anthropic, Ollama, etc.)
- Customizable research parameters (depth, breadth, concurrency)
- Knowledge base with vector storage and semantic search
- Report export to Markdown, PDF, DOCX, HTML
- User management with cost tracking
- Async task processing with Celery

## Project Structure

```
my-researcher/
├── backend/           # FastAPI backend
│   ├── app/
│   ├── tests/
│   └── requirements.txt
├── frontend/          # Next.js frontend (to be implemented)
├── docs/             # Design documentation
├── reference/        # Experimental code reference
├── docker-compose.yml
└── README.md
```

## Quick Start

### 🚀 Quick Start (5 minutes)

See [QUICKSTART.md](QUICKSTART.md) for a simplified setup guide.

### Option 1: Local Development (No Docker)

**Requirements:**
- Python 3.10+
- SQLite (included) or PostgreSQL (optional)

```bash
cd backend

# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp ../.env.local .env
# Edit .env and set OPENAI_API_KEY

# Initialize database
python scripts/init_db.py

# Start server
python scripts/dev.py
```

📖 **Detailed Guide:** [backend/LOCAL_SETUP.md](backend/LOCAL_SETUP.md)

### Option 2: Docker Compose

**Prerequisites:**
- Docker and Docker Compose
- OpenAI API key (or compatible API)

```bash
# Clone repository
git clone https://github.com/your-username/my-researcher.git
cd my-researcher

# Copy environment file
cp .env.example .env

# Edit .env with your API keys
nano .env

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

### Local Development

See [backend/README.md](backend/README.md) for detailed local development instructions.

## Documentation

- [Backend Design](docs/backend-design.md) - Complete backend architecture
- [Frontend UX Design](docs/GPT-Researcher前端UX设计方案.md) - Frontend design specification
- [Function Coverage](docs/后端功能覆盖总结.md) - Feature coverage matrix

## API Documentation

Once running:
- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

## Configuration

### LLM Providers

Supports multiple LLM providers:

```bash
# OpenAI
FAST_LLM=openai:gpt-4o-mini
SMART_LLM=openai:gpt-4o

# Anthropic Claude
SMART_LLM=anthropic:claude-3-opus-20240229

# Ollama (local)
FAST_LLM=ollama:llama2

# OpenAI-compatible (e.g., SiliconFlow)
FAST_LLM=openai:Qwen/Qwen3-8B
OPENAI_BASE_URL=https://api.siliconflow.cn/v1
```

### Retrievers

Multiple search options:

```bash
# Tavily (recommended)
RETRIEVER=tavily
TAVILY_API_KEY=your-key

# DuckDuckGo (free, no key)
RETRIEVER=ddg

# SearXNG (self-hosted)
RETRIEVER=searxng
SEARXNG_URL=http://localhost:8888
```

### Research Parameters

```bash
DEEP_RESEARCH_BREADTH=5     # Number of subtopics
DEEP_RESEARCH_DEPTH=3       # Research layers
DEEP_RESEARCH_CONCURRENCY=4 # Parallel queries
TEMPERATURE=0.4             # LLM temperature
LANGUAGE=english            # Report language
TOTAL_WORDS=2000           # Target word count
```

## Architecture

### Backend Stack
- FastAPI - Web framework
- PostgreSQL - Database
- Redis - Cache and message broker
- Celery - Task queue
- WebSocket - Real-time communication
- gpt-researcher - Research framework

### Frontend Stack (Planned)
- Next.js 14 - React framework
- shadcn/ui - UI components
- TailwindCSS - Styling
- Framer Motion - Animations

## Development Status

### Completed ✅
- Backend API structure
- Database models and schemas
- WebSocket progress service
- Research executor
- Docker configuration
- Authentication framework
- Configuration management

### In Progress 🚧
- Celery task integration
- Document processing
- Report export functionality

### Planned 📋
- Frontend implementation
- User management UI
- Knowledge base UI
- Advanced analytics

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Acknowledgments

Built on top of the excellent [gpt-researcher](https://github.com/assafelovic/gpt-researcher) framework.
