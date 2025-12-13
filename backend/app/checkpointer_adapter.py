from .persistence import SessionLocal
from .models import BlackboardState


def checkpoint_state(state: dict):
    db = SessionLocal()

    bb = BlackboardState(
        request_id=state["request_id"],
        version=state["version"],
        draft_text=state["draft_text"],
        safety_score=state["safety_score"],
        empathy_score=state["empathy_score"],
        iteration=state["iteration"],
        notes=state["notes"],
    )

    db.add(bb)
    db.commit()
    db.close()
