import uuid
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from backend.agent.graph import run_agent

logger = logging.getLogger("daton.api.chat")

router = APIRouter(prefix="/api/chat", tags=["chat"])

sessions: Dict[str, List[Any]] = {}


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    sources: List[str] = []
    chart_path: Optional[str] = None
    tools_used: List[str] = []


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())

    if session_id not in sessions:
        sessions[session_id] = []

    logger.info("Chat request [%s]: %s", session_id[:8], request.message[:100])

    try:
        result = run_agent(
            user_message=request.message,
            messages=sessions[session_id],
            session_id=session_id,
        )
        sessions[session_id] = result["messages"]
        logger.info("Chat response [%s]: tools=%s", session_id[:8], result.get("tools_used", []))

        return ChatResponse(
            response=result["response"],
            session_id=session_id,
            sources=result.get("sources", []),
            chart_path=result.get("chart_path"),
            tools_used=result.get("tools_used", []),
        )
    except Exception as e:
        logger.error("Agent error [%s]: %s", session_id[:8], e)
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


@router.delete("/{session_id}")
def clear_session(session_id: str):
    if session_id in sessions:
        del sessions[session_id]
    return {"status": "cleared"}
