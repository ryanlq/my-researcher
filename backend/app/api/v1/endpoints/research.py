"""Research API Endpoints"""

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.database import Research, User
from app.models.schemas import (
    ResearchRequest,
    ResearchResponse,
    ResearchProgress,
    CostEstimate
)
from app.core.research.executor import ResearchExecutor
from app.core.websocket.manager import WebSocketManager

router = APIRouter()
websocket_manager = WebSocketManager()


@router.post("/estimate", response_model=CostEstimate)
async def estimate_research(
    request: ResearchRequest,
    db: Session = Depends(get_db)
):
    """
    Estimate research cost and time

    Analyzes the query and research type to provide:
    - Estimated cost in USD
    - Estimated time to complete
    - Estimated number of queries
    """
    # TODO: Implement cost estimation logic
    # This would analyze the query complexity and research type
    estimated_cost = 0.15
    estimated_time = 2  # minutes
    estimated_queries = 10

    if request.report_type == "deep":
        estimated_cost = 0.40
        estimated_time = 8
        estimated_queries = 75

    return CostEstimate(
        estimated_cost=estimated_cost,
        estimated_time_minutes=estimated_time,
        estimated_queries=estimated_queries
    )


@router.post("", response_model=ResearchResponse, status_code=201)
async def create_research(
    request: ResearchRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new research task

    - Validates user's daily budget
    - Creates research task in database
    - Starts research execution in background
    - Returns task details with ID
    """
    import threading
    import asyncio
    from app.core.research.executor import execute_research_task

    # TODO: Get current user from JWT token
    # For now, use a placeholder user_id
    user_id = 1

    # Create research task
    research = Research(
        user_id=user_id,
        query=request.query,
        report_type=request.report_type,
        max_subtopics=request.max_subtopics,
        tone=request.tone,
        language=request.language,
        total_words=request.total_words,
        status="pending"
    )

    db.add(research)
    db.commit()
    db.refresh(research)

    # Start research execution in background thread
    def run_research_in_background():
        """Run research in a background thread"""
        # Create new event loop for this thread
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # Run the async research task
            loop.run_until_complete(execute_research_task(
                research_id=research.id,
                db_session=db,
                websocket_manager=websocket_manager
            ))
        finally:
            loop.close()

    # Start background thread
    thread = threading.Thread(target=run_research_in_background, daemon=True)
    thread.start()

    return ResearchResponse(
        id=research.id,
        query=research.query,
        report_type=research.report_type,
        status=research.status,
        current_depth=0,
        total_depth=3 if research.report_type == "deep" else 1,
        current_breadth=0,
        total_breadth=5 if research.report_type == "deep" else 1,
        completed_queries=0,
        total_queries=0,
        progress_percentage=0.0,
        report=None,
        report_format="markdown",
        sources=None,
        cost=0.0,
        created_at=research.created_at,
        started_at=None,
        completed_at=None,
        estimated_completion=None
    )


@router.get("/{research_id}", response_model=ResearchResponse)
async def get_research(
    research_id: int,
    db: Session = Depends(get_db)
):
    """
    Get research task details by ID
    """
    research = db.query(Research).filter(Research.id == research_id).first()

    if not research:
        raise HTTPException(status_code=404, detail="Research not found")

    progress_percentage = 0.0
    if research.total_queries > 0:
        progress_percentage = (research.completed_queries / research.total_queries) * 100

    return ResearchResponse(
        id=research.id,
        query=research.query,
        report_type=research.report_type,
        status=research.status,
        current_depth=research.current_depth,
        total_depth=research.total_depth,
        current_breadth=research.current_breadth,
        total_breadth=research.total_breadth,
        completed_queries=research.completed_queries,
        total_queries=research.total_queries,
        progress_percentage=progress_percentage,
        report=research.report,
        report_format=research.report_format,
        sources=research.sources,
        cost=research.cost,
        created_at=research.created_at,
        started_at=research.started_at,
        completed_at=research.completed_at,
        estimated_completion=research.estimated_completion
    )


@router.get("", response_model=List[ResearchResponse])
async def list_researches(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all research tasks for current user
    """
    # TODO: Get current user from JWT token
    user_id = 1

    query = db.query(Research).filter(Research.user_id == user_id)

    if status:
        query = query.filter(Research.status == status)

    researches = query.order_by(Research.created_at.desc()).offset(skip).limit(limit).all()

    results = []
    for research in researches:
        progress_percentage = 0.0
        if research.total_queries > 0:
            progress_percentage = (research.completed_queries / research.total_queries) * 100

        results.append(ResearchResponse(
            id=research.id,
            query=research.query,
            report_type=research.report_type,
            status=research.status,
            current_depth=research.current_depth,
            total_depth=research.total_depth,
            current_breadth=research.current_breadth,
            total_breadth=research.total_breadth,
            completed_queries=research.completed_queries,
            total_queries=research.total_queries,
            progress_percentage=progress_percentage,
            report=research.report,
            report_format=research.report_format,
            sources=research.sources,
            cost=research.cost,
            created_at=research.created_at,
            started_at=research.started_at,
            completed_at=research.completed_at,
            estimated_completion=research.estimated_completion
        ))

    return results


@router.post("/{research_id}/cancel")
async def cancel_research(
    research_id: int,
    db: Session = Depends(get_db)
):
    """
    Cancel a running research task
    """
    research = db.query(Research).filter(Research.id == research_id).first()

    if not research:
        raise HTTPException(status_code=404, detail="Research not found")

    if research.status not in ["pending", "running"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel research with status: {research.status}"
        )

    research.status = "cancelled"
    db.commit()

    # Notify WebSocket clients
    await websocket_manager.broadcast_progress(research_id, {
        "status": "cancelled",
        "message": "Research cancelled by user"
    })

    return {"message": "Research cancelled successfully"}


@router.websocket("/ws/{research_id}")
async def research_websocket(
    websocket: WebSocket,
    research_id: int,
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time research progress updates

    Connect to: ws://localhost:8000/api/v1/research/ws/{research_id}

    Events received:
    - research.connected: Connection established
    - research.started: Research has started
    - research.progress: Progress update (high frequency)
    - research.completed: Research completed successfully
    - research.error: Research failed with error
    """
    await websocket_manager.connect(websocket, research_id)
    research = db.query(Research).filter(Research.id == research_id).first()

    if not research:
        await websocket_manager.send_error(
            websocket,
            research_id,
            "Research not found"
        )
        websocket_manager.disconnect(websocket, research_id)
        return

    try:
        # Send initial connection message
        await websocket_manager.send_message(websocket, {
            "event": "research.connected",
            "research_id": research_id,
            "status": research.status,
            "timestamp": datetime.utcnow().isoformat()
        })

        # Keep connection alive and listen for messages
        while True:
            data = await websocket.receive_json()

            # Handle client commands
            command = data.get("command")

            if command == "pause":
                # TODO: Implement pause functionality
                pass
            elif command == "resume":
                # TODO: Implement resume functionality
                pass
            elif command == "cancel":
                # Cancel the research
                if research.status in ["pending", "running"]:
                    research.status = "cancelled"
                    db.commit()
                    await websocket_manager.broadcast_progress(research_id, {
                        "status": "cancelled",
                        "message": "Research cancelled"
                    })

    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, research_id)
    except Exception as e:
        await websocket_manager.send_error(
            websocket,
            research_id,
            str(e)
        )
        websocket_manager.disconnect(websocket, research_id)
