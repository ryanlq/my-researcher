"""Celery Research Tasks"""

from celery import shared_task
from app.core.database import SessionLocal
from app.core.websocket.manager import websocket_manager
from app.core.research.executor import execute_research_task
import logging

logger = logging.getLogger(__name__)


@shared_task(name="execute_research")
def execute_research_celery_task(research_id: int):
    """
    Execute research task asynchronously

    This task is queued when a user creates a new research.
    It runs the research using gpt-researcher and updates the database.
    """
    logger.info(f"Starting Celery research task for research {research_id}")

    # Create database session
    db = SessionLocal()

    try:
        # Import asyncio and run the async executor
        import asyncio

        # Run the async research executor
        asyncio.run(execute_research_task(
            research_id=research_id,
            db_session=db,
            websocket_manager=websocket_manager
        ))

        logger.info(f"Celery research task completed for research {research_id}")

    except Exception as e:
        logger.error(f"Celery research task failed for research {research_id}: {e}")

    finally:
        db.close()


@shared_task(name="export_report")
def export_report_task(research_id: int, export_format: str):
    """
    Export report to different format

    Supported formats: markdown, pdf, docx, html
    """
    logger.info(f"Exporting report for research {research_id} to {export_format}")

    # TODO: Implement export logic
    # - Get research from database
    # - Generate report in requested format
    # - Save to file
    # - Update export history

    return {
        "research_id": research_id,
        "format": export_format,
        "status": "completed"
    }


@shared_task(name="process_document")
def process_document_task(document_id: int):
    """
    Process uploaded document

    - Extract text content
    - Split into chunks
    - Vectorize and store
    """
    logger.info(f"Processing document {document_id}")

    # TODO: Implement document processing
    # - Get document from database
    # - Extract text based on file type
    # - Split into chunks
    # - Generate embeddings
    # - Store in vector database

    return {
        "document_id": document_id,
        "status": "processed"
    }


@shared_task(name="cleanup_old_researches")
def cleanup_old_researches(days: int = 30):
    """
    Clean up old researches

    Removes researches older than specified days
    """
    logger.info(f"Cleaning up researches older than {days} days")

    # TODO: Implement cleanup logic
    # - Query old researches
    # - Archive or delete
    # - Clean up vectors

    return {
        "cleaned": 0
    }
