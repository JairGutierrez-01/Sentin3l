from fastapi import FastAPI
from sentin3l.config import settings

app = FastAPI(
    title=settings.project_name,
    version=settings.version,
)


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