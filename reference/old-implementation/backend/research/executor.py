"""Research Execution Core"""

import asyncio
import json
from typing import Optional, Callable, Awaitable
from datetime import datetime, timedelta
import logging

from gpt_researcher import GPTResearcher
from app.core.config import settings
from app.core.websocket.manager import WebSocketManager
from app.models.database import Research

logger = logging.getLogger(__name__)


class ResearchExecutor:
    """
    Executes research tasks using gpt-researcher
    """

    def __init__(self, websocket_manager: WebSocketManager):
        self.websocket_manager = websocket_manager

    async def execute_research(
        self,
        research: Research,
        on_progress: Optional[Callable[[dict], Awaitable[None]]] = None
    ) -> dict:
        """
        Execute a research task

        Args:
            research: Research database model
            on_progress: Optional callback for progress updates

        Returns:
            dict with research results
        """
        logger.info(f"Starting research {research.id}: {research.query}")

        # Configure gpt-researcher
        mcp_configs = []

        # TODO: Load MCP configs from user settings
        # For now, use the reference implementation
        mcp_configs.append({
            "name": "searxng-search",
            "command": "python",
            "args": ["reference/web_search_mcp.py"],
            "env": {"SEARXNG_URL": "http://127.0.0.1:8888"}
        })

        # Create researcher instance
        researcher = GPTResearcher(
            query=research.query,
            report_type=research.report_type,
            report_format=research.report_format or "markdown",
            tone=research.tone,
            mcp_configs=mcp_configs,
            mcp_strategy="deep" if research.report_type == "deep" else "auto",
            max_subtopics=research.max_subtopics,
            verbose=True
        )

        # Custom progress handler
        async def handle_progress(progress_data):
            """
            Handle progress updates from gpt-researcher
            """
            logger.debug(f"Progress: {progress_data}")

            # Update research in database
            if "current_depth" in progress_data:
                research.current_depth = progress_data.get("current_depth", 0)
            if "current_breadth" in progress_data:
                research.current_breadth = progress_data.get("current_breadth", 0)
            if "completed_queries" in progress_data:
                research.completed_queries = progress_data.get("completed_queries", 0)
            if "cost" in progress_data:
                research.cost = progress_data.get("cost", 0.0)

            # Broadcast via WebSocket
            await self.websocket_manager.broadcast_progress(
                research.id,
                progress_data
            )

            # Call custom callback
            if on_progress:
                await on_progress(progress_data)

        # Execute research
        try:
            # Broadcast started
            await self.websocket_manager.broadcast_started(
                research.id,
                estimated_time_minutes=5 if research.report_type == "deep" else 2
            )

            # Conduct research
            await researcher.conduct_research()

            # Generate report
            report = await researcher.write_report()

            # Get sources and context
            sources = researcher.get_research_sources()
            context = researcher.get_research_context()

            # Update research with results
            research.report = report
            research.sources = sources
            research.context = context
            research.status = "completed"
            research.completed_at = datetime.utcnow()

            # Broadcast completion
            await self.websocket_manager.broadcast_completed(
                research.id,
                report
            )

            logger.info(f"Research {research.id} completed successfully")

            return {
                "report": report,
                "sources": sources,
                "context": context,
                "cost": research.cost
            }

        except Exception as e:
            logger.error(f"Research {research.id} failed: {e}")
            research.status = "failed"

            # Broadcast error
            await self.websocket_manager.broadcast_to_research(
                research.id,
                {
                    "event": "research.error",
                    "research_id": research.id,
                    "error": str(e)
                }
            )

            raise

    async def estimate_cost(self, query: str, report_type: str) -> dict:
        """
        Estimate research cost and time

        Args:
            query: Research query
            report_type: Type of research report

        Returns:
            dict with cost, time, and query estimates
        """
        # Base estimates
        base_cost = 0.10
        base_time = 2  # minutes
        base_queries = 10

        # Adjust based on report type
        if report_type == "deep":
            base_cost = 0.40
            base_time = 8
            base_queries = 75
        elif report_type == "multi_agent":
            base_cost = 0.60
            base_time = 15
            base_queries = 100

        # Adjust based on query complexity (simple heuristic)
        query_length = len(query)
        if query_length > 200:
            base_cost *= 1.5
            base_time *= 1.3
            base_queries *= 1.2

        return {
            "estimated_cost": round(base_cost, 2),
            "estimated_time_minutes": int(base_time),
            "estimated_queries": int(base_queries)
        }


async def execute_research_task(
    research_id: int,
    db_session,
    websocket_manager: WebSocketManager
):
    """
    Celery task wrapper for executing research

    This function is designed to be called from a Celery task
    """
    from app.models.database import Research
    from sqlalchemy.orm import sessionmaker

    # Create new session for this task
    Session = sessionmaker(bind=db_session.bind)
    db = Session()

    try:
        # Get research from database
        research = db.query(Research).filter(Research.id == research_id).first()

        if not research:
            logger.error(f"Research {research_id} not found")
            return

        # Update status
        research.status = "running"
        research.started_at = datetime.utcnow()
        db.commit()

        # Execute research
        executor = ResearchExecutor(websocket_manager)
        await executor.execute_research(research)

        # Commit final changes
        db.commit()

    except Exception as e:
        logger.error(f"Research task failed: {e}")
        research.status = "failed"
        db.commit()

    finally:
        db.close()
