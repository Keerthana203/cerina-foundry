from fastapi import FastAPI
from .persistence import init_db

app = FastAPI(title="Cerina Protocol Foundry")

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/health")
def health():
    return {"status": "ok"}
