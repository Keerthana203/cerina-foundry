"""
MCP Tool Wrapper for Cerina Protocol Foundry

This exposes the system as an MCP-compatible tool
without duplicating business logic.
"""

from typing import Dict, Any
import time

from .persistence import SessionLocal
from .models import ProtocolRequest, BlackboardState
from .pipeline_runner import run_pipeline


def run_protocol_tool(input: Dict[str, Any]) -> Dict[str, Any]:
    """
    MCP entry point.

    Expected input:
    {
        "prompt": "Create a sleep hygiene protocol"
    }
    """

    prompt = input.get("prompt")
    if not prompt:
        return {"error": "Missing 'prompt' field"}

    db = SessionLocal()

    try:


        # 1. Create protocol request
        req = ProtocolRequest(
            user_intent=prompt,
            status="running"
        )
        db.add(req)
        db.commit()
        db.refresh(req)

        request_id = req.id

        # 2. Run pipeline synchronously (MCP-friendly)
        run_pipeline(request_id, prompt)

        # 3. Fetch final state
        final_state = (
            db.query(BlackboardState)
            .filter(BlackboardState.request_id == request_id)
            .order_by(BlackboardState.version.desc())
            .first()
        )
    finally:

        db.close()

    if not final_state:
        return {
            "request_id": request_id,
            "status": "running",
            "status_url": f"/state/{request_id}",
        }

    return {
        "request_id": request_id,
        "status": "completed",
        "final_text": final_state.draft_text,
        "safety_score": final_state.safety_score,
        "empathy_score": final_state.empathy_score,
    }
