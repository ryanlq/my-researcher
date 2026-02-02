# GPT-Researcher Backend

AI-powered research automation platform built with FastAPI and gpt-researcher.

## Features

- **Multiple Research Modes**: Standard, Deep, Multi-Agent, Knowledge Base
- **Real-time Progress**: WebSocket updates during research
- **User Management**: Authentication, authorization, cost tracking
- **Knowledge Base**: Document upload, vector storage, semantic search
- **Report Export**: Markdown, PDF, DOCX, HTML
- **Task Queue**: Celery for async research execution

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL + SQLAlchemy
- **Cache/Queue**: Redis + Celery
- **Real-time**: WebSocket
- **Vector Store**: FAISS / Qdrant
- **Research**: gpt-researcher

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/    # API route handlers
│   │       └── __init__.py
│   ├── core/
│   │   ├── config.py         # Configuration
│   │   ├── database.py       # Database connection
│   │   ├── redis.py          # Redis connection
│   │   ├── research/         # Research execution
│   │   ├── security/         # Authentication
│   │   └── websocket/        # WebSocket manager
│   ├── models/
│   │   ├── database.py       # SQLAlchemy models
│   │   └── schemas.py        # Pydantic schemas
│   ├── services/             # Business logic
│   ├── tasks/                # Celery tasks
│   ├── utils/                # Utilities
│   └── main.py               # FastAPI app
├── tests/
├── scripts/
├── requirements.txt
├── Dockerfile
└── README.md
```

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Copy environment file
cp .env.example .env

# Edit .env with your API keys
nano .env

# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

### Local Development

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Set up PostgreSQL
createdb gpt_researcher

# Set environment variables
export DATABASE_URL="postgresql://user:pass@localhost/gpt_researcher"
export OPENAI_API_KEY="sk-..."

# Run database migrations
alembic upgrade head

# Run the server
uvicorn app.main:app --reload
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

## API Endpoints

### Research
- `POST /api/v1/research/estimate` - Estimate research cost
- `POST /api/v1/research` - Create research task
- `GET /api/v1/research/{id}` - Get research details
- `GET /api/v1/research` - List researches
- `POST /api/v1/research/{id}/cancel` - Cancel research
- `WS /api/v1/research/ws/{id}` - WebSocket for real-time progress

### Authentication
- `POST /api/v1/auth/register` - Register user
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Get current user

### Documents
- `POST /api/v1/documents/upload` - Upload documents
- `GET /api/v1/documents` - List documents
- `DELETE /api/v1/documents/{id}` - Delete document

### Configuration
- `GET /api/v1/config/llm` - Get LLM config
- `PUT /api/v1/config/llm` - Update LLM config
- `GET /api/v1/config/retriever` - Get retriever config
- `PUT /api/v1/config/retriever` - Update retriever config

### Exports
- `POST /api/v1/exports` - Export report
- `GET /api/v1/exports/{id}/download` - Download export

## WebSocket Events

### Client → Server
- `start` - Start research
- `pause` - Pause research
- `resume` - Resume research
- `cancel` - Cancel research

### Server → Client
- `research.connected` - Connection established
- `research.started` - Research started
- `research.progress` - Progress update
- `research.completed` - Research completed
- `research.error` - Research error

## Configuration

### LLM Providers

Supports multiple providers:
- OpenAI
- Anthropic (Claude)
- Ollama (local)
- DeepSeek
- Groq
- Mistral AI
- Any OpenAI-compatible API

Set in `.env`:
```
FAST_LLM=openai:gpt-4o-mini
SMART_LLM=openai:gpt-4o
STRATEGIC_LLM=anthropic:claude-3-opus-20240229
EMBEDDING=openai:text-embedding-3-small
```

### Retrievers

Supported retrievers:
- Tavily (requires API key)
- Google Search (requires API key)
- Bing Search (requires API key)
- DuckDuckGo (free)
- SearXNG (self-hosted)
- MCP (custom)

Set in `.env`:
```
RETRIEVER=tavily
TAVILY_API_KEY=your-tavily-key
```

### Research Parameters

Adjust in `.env`:
```
DEEP_RESEARCH_BREADTH=5     # Number of subtopics
DEEP_RESEARCH_DEPTH=3       # Layers of research
DEEP_RESEARCH_CONCURRENCY=4 # Parallel queries
MAX_SUBTOPICS=5
TEMPERATURE=0.4
LANGUAGE=english
TOTAL_WORDS=2000
```

## Development

### Running Tests

```bash
pytest tests/
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Celery Monitoring

Access Flower at: http://localhost:5555

## License

MIT
