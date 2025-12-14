from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from threading import Thread

from .persistence import init_db, SessionLocal
from .models import ProtocolRequest, BlackboardState
from .pipeline_runner import run_pipeline
from fastapi.responses import StreamingResponse
import time
import json
from pydantic import BaseModel

app = FastAPI(title="Cerina Protocol Foundry")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


class StartRequest(BaseModel):
    intent: str
class DeclineRequest(BaseModel):
    reason: str | None = None
class RerunRequest(BaseModel):
    feedback: str


@app.post("/start")
def start_protocol(req: StartRequest):
    db = SessionLocal()

    protocol = ProtocolRequest(user_intent=req.intent, status="running")
    db.add(protocol)
    db.commit()
    db.refresh(protocol)
    db.close()

    thread = Thread(
        target=run_pipeline,
        args=(protocol.id, req.intent),
        daemon=True,
    )
    thread.start()

    return {"request_id": protocol.id}


@app.get("/state/{request_id}")
def get_latest_state(request_id: int):
    db = SessionLocal()

    state = (
        db.query(BlackboardState)
        .filter(BlackboardState.request_id == request_id)
        .order_by(BlackboardState.version.desc())
        .first()
    )

    db.close()

    if not state:
        raise HTTPException(status_code=404, detail="No state found")

    return {
        "version": state.version,
        "draft_text": state.draft_text,
        "safety_score": state.safety_score,
        "empathy_score": state.empathy_score,
        "iteration": state.iteration,
        "notes": state.notes,
        "finalized": state.finalized,
    }


@app.post("/halt/{request_id}")
def halt_protocol(request_id: int):
    db = SessionLocal()

    req = db.query(ProtocolRequest).get(request_id)
    if not req:
        db.close()
        raise HTTPException(status_code=404, detail="Request not found")

    req.status = "halted"
    db.commit()
    db.close()

    return {"status": "halted"}


class ApproveRequest(BaseModel):
    final_text: str


@app.post("/approve/{request_id}")
def approve_protocol(request_id: int, body: ApproveRequest):
    db = SessionLocal()

    req = db.query(ProtocolRequest).get(request_id)
    if not req:
        db.close()
        raise HTTPException(status_code=404, detail="Request not found")

    state = BlackboardState(
        request_id=request_id,
        version=9999,
        draft_text=body.final_text,
        finalized=True,
        notes=[{"agent": "human", "message": "Protocol approved"}],
    )

    req.status = "approved"

    db.add(state)
    db.commit()
    db.close()

    return {"status": "approved"}

@app.get("/stream/{request_id}")
def stream_protocol(request_id: int):
    def event_generator():
        # 🔥 FIX: start streaming from the latest known version
        db = SessionLocal()
        latest = (
            db.query(BlackboardState)
            .filter(BlackboardState.request_id == request_id)
            .order_by(BlackboardState.version.desc())
            .first()
        )
        last_version = latest.version if latest else 0
        db.close()

        while True:
            db = SessionLocal()

            state = (
                db.query(BlackboardState)
                .filter(
                    BlackboardState.request_id == request_id,
                    BlackboardState.version > last_version,
                )
                .order_by(BlackboardState.version.asc())
                .first()
            )

            db.close()

            if state:
                last_version = state.version

                payload = {
                    "version": state.version,
                    "draft_text": state.draft_text,
                    "notes": state.notes,
                    "safety_score": state.safety_score,
                    "empathy_score": state.empathy_score,
                    "finalized": state.finalized,
                }

                yield f"data: {json.dumps(payload)}\n\n"

                if state.finalized:
                    break

            time.sleep(1)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )



@app.post("/decline/{request_id}")
def decline_protocol(request_id: int, body: DeclineRequest | None = None):
    db = SessionLocal()

    req = db.query(ProtocolRequest).get(request_id)
    if not req:
        db.close()
        raise HTTPException(status_code=404, detail="Request not found")

    # Update request status
    req.status = "declined"

    # Record human decision in blackboard
    decline_note = {
        "agent": "human",
        "message": f"Protocol declined. Reason: {body.reason if body else 'Not specified'}"
    }

    state = BlackboardState(
        request_id=request_id,
        version=9998,  # reserved pre-final human decision
        draft_text="",
        finalized=False,
        notes=[decline_note],
    )

    db.add(state)
    db.commit()
    db.close()

    return {"status": "declined"}


@app.post("/rerun/{request_id}")
def rerun_protocol(request_id: int, body: RerunRequest):
    db = SessionLocal()

    req = db.query(ProtocolRequest).get(request_id)
    if not req:
        db.close()
        raise HTTPException(status_code=404, detail="Request not found")

    user_intent = req.user_intent

    if req.status == "approved":
        db.close()
        raise HTTPException(
            status_code=400,
            detail="Cannot rerun an approved protocol"
        )

    latest_state = (
        db.query(BlackboardState)
        .filter(BlackboardState.request_id == request_id)
        .order_by(BlackboardState.version.desc())
        .first()
    )

    notes = list(latest_state.notes if latest_state else [])
    notes.append({
        "agent": "human",
        "message": f"Revision requested: {body.feedback}"
    })

    base_state = {
        "request_id": request_id,
        "version": latest_state.version + 1,
        "user_intent": user_intent,
        "draft_text": latest_state.draft_text,
        "iteration": latest_state.iteration,
        "safety_score": latest_state.safety_score,
        "empathy_score": latest_state.empathy_score,
        "notes": notes,
    }

    feedback_state = BlackboardState(
        request_id=request_id,
        version=base_state["version"],
        draft_text=base_state["draft_text"],
        iteration=base_state["iteration"],
        safety_score=base_state["safety_score"],
        empathy_score=base_state["empathy_score"],
        notes=base_state["notes"],
        finalized=False,
    )

    db.add(feedback_state)
    req.status = "running"
    db.commit()
    db.close()

    Thread(
        target=run_pipeline,
        args=(request_id, user_intent, base_state),
        daemon=True,
    ).start()

    return { "status": "rerunning",
    "base_version": base_state["version"]}
