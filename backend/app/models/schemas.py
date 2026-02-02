"""Pydantic Schemas for API"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# =====================
# Research Schemas
# =====================

class ResearchStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class ReportFormat(str, Enum):
    MARKDOWN = "markdown"
    PDF = "pdf"
    DOCX = "docx"
    HTML = "html"


class ReportSource(str, Enum):
    """研究来源类型"""
    WEB = "web"                  # 全网搜索（默认）
    STATIC = "static"            # 指定URL
    LOCAL = "local"              # 本地文档
    HYBRID = "hybrid"            # 混合模式（URL + 本地）


class ResearchRequest(BaseModel):
    """Request to create a new research"""
    query: str = Field(..., min_length=3, max_length=2000, description="Research query")
    report_type: str = Field(default="research_report", description="Type of report")
    max_subtopics: Optional[int] = Field(default=5, ge=1, le=10)
    tone: Optional[str] = Field(default="Analytical")
    language: Optional[str] = Field(default="english")
    total_words: Optional[int] = Field(default=2000, ge=500, le=10000)
    custom_prompt: Optional[str] = None

    # 指定来源研究相关字段
    report_source: Optional[ReportSource] = Field(
        default=ReportSource.WEB,
        description="研究来源类型: web(全网), static(指定URL), local(本地文档), hybrid(混合)"
    )
    source_urls: Optional[List[str]] = Field(
        default=None,
        description="指定研究的URL列表（STATIC/HYBRID模式需要）"
    )
    complement_source_urls: bool = Field(
        default=False,
        description="是否在指定URL外进行全网补充搜索"
    )
    document_ids: Optional[List[int]] = Field(
        default=None,
        description="本地文档ID列表（LOCAL/HYBRID模式需要）"
    )


class ResearchResponse(BaseModel):
    """Research response"""
    id: int
    query: str
    report_type: str
    status: ResearchStatus

    # Progress
    current_depth: int
    total_depth: int
    current_breadth: int
    total_breadth: int
    completed_queries: int
    total_queries: int
    progress_percentage: float

    # Results
    report: Optional[str] = None
    report_format: str
    sources: Optional[List[Dict]] = None
    cost: float

    # Timestamps
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None

    class Config:
        from_attributes = True


class ResearchProgress(BaseModel):
    """Research progress update"""
    research_id: int
    status: ResearchStatus
    current_depth: int
    total_depth: int
    current_breadth: int
    total_breadth: int
    completed_queries: int
    total_queries: int
    current_query: Optional[str] = None
    cost: float
    progress_percentage: float
    message: Optional[str] = None


# =====================
# User Schemas
# =====================

class UserCreate(BaseModel):
    """User registration"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    """User login"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response"""
    id: int
    email: str
    full_name: Optional[str] = None
    is_active: bool
    is_premium: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT Token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# =====================
# Document Schemas
# =====================

class DocumentUpload(BaseModel):
    """Document upload metadata"""
    filename: str
    title: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class DocumentResponse(BaseModel):
    """Document response"""
    id: int
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    chunk_count: int
    is_processed: bool
    metadata: Optional[Dict] = None
    uploaded_at: datetime

    class Config:
        from_attributes = True


# =====================
# Configuration Schemas
# =====================

class LLMConfig(BaseModel):
    """LLM Configuration"""
    fast_llm: str
    smart_llm: str
    strategic_llm: str
    embedding: str
    openai_api_key: Optional[str] = None
    openai_base_url: Optional[str] = None


class RetrieverConfig(BaseModel):
    """Retriever Configuration"""
    retriever: str
    tavily_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    google_cx: Optional[str] = None
    bing_api_key: Optional[str] = None


class ResearchConfig(BaseModel):
    """Research Parameters"""
    deep_research_breadth: int = Field(default=5, ge=1, le=10)
    deep_research_depth: int = Field(default=3, ge=1, le=5)
    deep_research_concurrency: int = Field(default=4, ge=1, le=10)
    max_subtopics: int = Field(default=5, ge=1, le=10)
    temperature: float = Field(default=0.4, ge=0.0, le=1.0)
    language: str = "english"
    total_words: int = Field(default=2000, ge=500, le=10000)


class UserConfigUpdate(BaseModel):
    """User configuration update"""
    llm_config: Optional[LLMConfig] = None
    retriever_config: Optional[RetrieverConfig] = None
    research_config: Optional[ResearchConfig] = None


# =====================
# Export Schemas
# =====================

class ExportRequest(BaseModel):
    """Export report request"""
    research_id: int
    format: ReportFormat


class ExportResponse(BaseModel):
    """Export response"""
    id: int
    research_id: int
    format: ReportFormat
    file_path: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# =====================
# Common Schemas
# =====================

class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    version: str
    database: str
    redis: str


class ErrorMessage(BaseModel):
    """Error message"""
    detail: str


class CostEstimate(BaseModel):
    """Cost estimate for research"""
    estimated_cost: float
    estimated_time_minutes: int
    estimated_queries: int
