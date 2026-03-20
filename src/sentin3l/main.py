from fastapi import FastAPI, Request
from sentin3l.config import settings
from sentin3l.database.init_db import init_db
from pydantic import BaseModel, HttpUrl, Field, ValidationError
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sentin3l.api.schemas import AnalysisResponse
from typing import List
from sentin3l.database.session import get_db
from sentin3l.services import observed_resource_service, analysis_service
from sentin3l.utils.url_tools import process_url_for_storage
from sentin3l.api.schemas import AnalysisResponse
import os
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import traceback


app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")

static_dir = os.path.join(FRONTEND_DIR, "static")
templates_dir = os.path.join(FRONTEND_DIR, "templates")

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

init_db()

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/status")
def api_status():
    return {"api": "running"}

class AnalyzeRequest(BaseModel):
    url: HttpUrl = Field(..., description="URL to analyze", max_length=2048)


@app.post("/api/v1/analyze", response_model=AnalysisResponse)
def analyze_url(request: AnalyzeRequest, db: Session = Depends(get_db)):
    """
    Primary entry point for URL analysis.
    Processes the URL, applies security heuristics, and persists the results.
    """
    try:
        url_str = str(request.url)

        url_metadata = process_url_for_storage(url_str)

        resource = observed_resource_service.get_or_create_resource(db, url_str)

        analysis = analysis_service.create_analysis_for_resource(db, resource, url_str)

        return {
            "id": analysis.id,
            "target_url": url_str,
            "safe_url": url_metadata["safe_url"],
            "suspicion_score": analysis.suspicion_score,
            "risk_level": analysis.risk_level,
            "explanation_text": analysis.explanation_text,
            "recommendation_text": analysis.recommendation_text,
            "times_analyzed_before": resource.occurrence_count,
            "analyzed_at": analysis.analyzed_at,
            "flags": [
                {
                    "code": f.definition.code,
                    "evidence_summary": f.evidence_summary
                } for f in analysis.flags
            ]
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/recent", response_model=List[AnalysisResponse])
def get_recent_activity(db: Session = Depends(get_db), limit: int = 10):
    """
    Returns a global feed of the most recent analyses.
    Ideal for populating the main frontend table without requiring a login.
    """
    recent_list = analysis_service.get_recent_analyses(db, limit=limit)

    return [
        {
            **a.__dict__,
            "target_url": a.resource.hostname,  # for privacy, no raw_url
            "safe_url": "Propiedad de la DB o generada",
            "times_analyzed_before": a.resource.occurrence_count,
            "flags": [
                {
                    "code": f.definition.code,
                    "evidence_summary": f.evidence_summary
                } for f in a.flags
            ]
        } for a in recent_list
    ]