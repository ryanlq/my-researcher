"""Database Models"""

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class ResearchStatus(str, enum.Enum):
    """Research Status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class ReportFormat(str, enum.Enum):
    """Report Format"""
    MARKDOWN = "markdown"
    PDF = "pdf"
    DOCX = "docx"
    HTML = "html"


class User(Base):
    """User Model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Integer, default=1)
    is_premium = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    researches = relationship("Research", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")


class Research(Base):
    """Research Model"""
    __tablename__ = "researches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    query = Column(Text, nullable=False)
    report_type = Column(String(50), default="research_report")  # research_report, deep, multi_agent
    status = Column(Enum(ResearchStatus), default=ResearchStatus.PENDING)

    # Research Parameters
    max_subtopics = Column(Integer, default=5)
    tone = Column(String(50), default="Analytical")
    language = Column(String(20), default="english")
    total_words = Column(Integer, default=2000)

    # Progress Tracking
    current_depth = Column(Integer, default=0)
    total_depth = Column(Integer, default=3)
    current_breadth = Column(Integer, default=0)
    total_breadth = Column(Integer, default=5)
    completed_queries = Column(Integer, default=0)
    total_queries = Column(Integer, default=0)

    # Results
    report = Column(Text)
    report_format = Column(String(20), default="markdown")
    sources = Column(JSON)  # List of source URLs
    context = Column(Text)  # Research context
    cost = Column(Float, default=0.0)

    # Research Tree (for deep research)
    research_tree = Column(JSON)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    estimated_completion = Column(DateTime)

    # Relationships
    user = relationship("User", back_populates="researches")
    exports = relationship("ExportHistory", back_populates="research", cascade="all, delete-orphan")


class Document(Base):
    """Document Model (Knowledge Base)"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50))  # pdf, docx, txt, md, etc.
    file_size = Column(Integer)  # bytes

    # Processing
    content = Column(Text)  # Extracted text
    chunk_count = Column(Integer, default=0)
    is_processed = Column(Integer, default=0)

    # Metadata
    doc_metadata = Column(JSON)  # title, author, etc.
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="documents")


class APIKey(Base):
    """API Key Model"""
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    provider = Column(String(50), nullable=False)  # openai, anthropic, etc.
    api_key_encrypted = Column(String(500), nullable=False)
    base_url = Column(String(500))  # Custom base URL
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="api_keys")


class ExportHistory(Base):
    """Export History Model"""
    __tablename__ = "export_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    research_id = Column(Integer, ForeignKey("researches.id"), nullable=False)
    format = Column(Enum(ReportFormat), nullable=False)
    file_path = Column(String(500))
    file_size = Column(Integer)  # bytes
    status = Column(String(20), default="pending")  # pending, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    research = relationship("Research", back_populates="exports")


class UsageStats(Base):
    """Usage Statistics Model"""
    __tablename__ = "usage_stats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, nullable=False)

    # Daily Stats
    total_researches = Column(Integer, default=0)
    completed_researches = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)
    total_queries = Column(Integer, default=0)

    # Report Generation
    total_reports = Column(Integer, default=0)
    total_words = Column(Integer, default=0)


class ResearchHistory(Base):
    """Research History Model"""
    __tablename__ = "research_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    research_id = Column(Integer, ForeignKey("researches.id"), nullable=False)

    # Event Tracking
    event_type = Column(String(50), nullable=False)  # started, completed, failed, etc.
    event_data = Column(JSON)  # Additional event data
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
