from .langgraph_pipeline import build_graph
from .checkpointer_adapter import checkpoint_state
from .persistence import SessionLocal
from .models import ProtocolRequest

graph = build_graph()


def run_pipeline(request_id: int, initial_text: str):
    db = SessionLocal()

    state = {
        "request_id": request_id,
        "version": 1,
        "draft_text": initial_text,
        "iteration": 0,
        "safety_score": 1.0,
        "empathy_score": 0.0,
        "notes": [],
    }

    final_state = graph.invoke(state)
    final_state = {
        **final_state,
        "version": 1
    }
    checkpoint_state(final_state)

    req = db.query(ProtocolRequest).get(request_id)
    if req:
        req.status = "completed"
        db.commit()

    db.close()
