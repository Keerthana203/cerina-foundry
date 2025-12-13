from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from threading import Thread

from .persistence import init_db, SessionLocal
from .models import ProtocolRequest, BlackboardState
from .pipeline_runner import run_pipeline
from fastapi.responses import StreamingResponse
import time
import json


app = FastAPI(title="Cerina Protocol Foundry")


@app.on_event("startup")
def on_startup():
    init_db()


class StartRequest(BaseModel):
    intent: str


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
        last_version = 0

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
