"""Application Configuration"""

from pydantic_settings import BaseSettings
from typing import Optional, List, Union
from pydantic import field_validator


class Settings(BaseSettings):
    """Application Settings"""

    # Application
    APP_NAME: str = "GPT-Researcher API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/gpt_researcher"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # CORS
    CORS_ORIGINS: Union[str, List[str]] = ["http://localhost:3000", "http://localhost:8000"]

    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except:
                # 如果解析失败，按逗号分割
                return [origin.strip() for origin in v.split(',')]
        return v

    # LLM Configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: Optional[str] = None
    FAST_LLM: str = "openai:gpt-4o-mini"
    SMART_LLM: str = "openai:gpt-4o"
    STRATEGIC_LLM: str = "openai:o1-preview"
    EMBEDDING: str = "openai:text-embedding-3-small"
    EMBEDDING_KWARGS: str = '{"chunk_size": 64}'

    # Research Configuration
    RETRIEVER: str = "tavily"
    DEEP_RESEARCH_BREADTH: int = 5
    DEEP_RESEARCH_DEPTH: int = 3
    DEEP_RESEARCH_CONCURRENCY: int = 4
    MAX_SUBTOPICS: int = 5
    TEMPERATURE: float = 0.4
    LANGUAGE: str = "english"
    TOTAL_WORDS: int = 2000

    # Report Configuration
    REPORT_FORMAT: str = "markdown"
    REPORT_TONE: str = "Analytical"

    # Cost Management
    DEFAULT_DAILY_BUDGET: float = 5.0
    COST_WARNING_THRESHOLD: float = 0.8  # 80%

    # File Upload
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    UPLOAD_DIR: str = "uploads"

    # Document Path for GPT-Researcher local document research
    DOC_PATH: str = "data/documents"  # 本地文档存储路径

    # Vector Store
    VECTOR_STORE_TYPE: str = "faiss"  # faiss, qdrant, weaviate, pgvector
    VECTOR_STORE_PATH: str = "data/vectors"

    # Qdrant
    QDRANT_HOST: Optional[str] = "localhost"
    QDRANT_PORT: Optional[int] = 6333

    # MCP Configuration
    MCP_STRATEGY: str = "deep"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    # Rate Limiting
    DAILY_BUDGET_LIMIT: float = 10.0
    MAX_DAILY_RESEARCHES: int = 100

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    CELERY_WORKER_CONCURRENCY: int = 2
    CELERY_TASK_TIMEOUT: int = 3600

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # 忽略额外字段


settings = Settings()
