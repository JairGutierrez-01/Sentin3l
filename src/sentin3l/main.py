from fastapi import FastAPI
from sentin3l.config import settings
from sentin3l.database.init_db import init_db

app = FastAPI(
    title=settings.project_name,
    version=settings.version,
)

init_db()

@app.get("/")
def read_root():
    return {
        "status": "online",
        "system": settings.project_name,
        "version": settings.version,
        "debug": settings.debug,
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/status")
def api_status():
    return {"api": "running"}