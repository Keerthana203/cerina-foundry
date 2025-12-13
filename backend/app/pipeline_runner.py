from .langgraph_pipeline import build_graph
from .checkpointer_adapter import checkpoint_state
from .persistence import SessionLocal
from .models import ProtocolRequest

graph = build_graph()


def run_pipeline(request_id: int, user_intent: str):
    db = SessionLocal()

    req = db.query(ProtocolRequest).get(request_id)
    if not req or req.status != "running":
        db.close()
        return  # 🚨 prevent duplicate execution

    state = {
        "request_id": request_id,
        "version": 1,
        "user_intent": user_intent,
        "draft_text": "",
        "iteration": 0,
        "safety_score": 1.0,
        "empathy_score": 0.0,
        "notes": [],
    }

    final_state = graph.invoke(state)

    final_state["finalized"] = True
    final_state["version"] += 1
    checkpoint_state(final_state)

    req.status = "completed"
    db.commit()
    db.close()
