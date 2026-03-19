from fastapi import FastAPI
from sentin3l.config import settings
from sentin3l.database.init_db import init_db
from pydantic import BaseModel, HttpUrl, Field
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from sentin3l.database.session import get_db
from sentin3l.services import observed_resource_service, analysis_service

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

class AnalyzeRequest(BaseModel):
    url: HttpUrl = Field(..., description="URL to analyze", max_length=2048)


@app.post("/api/v1/analyze")
def analyze_url(request: AnalyzeRequest, db: Session = Depends(get_db)):
    """
    It receives a suspicious URL, processes it through detectors,
    and returns a security verdict.
    """
    try:
        url_str = str(request.url)
        # identity
        resource = observed_resource_service.get_or_create_resource(db, url_str)

        #analysis with rules
        analysis = analysis_service.create_analysis_for_resource(db, resource, url_str)

        # response
        return {
            "target_url": request.url,
            "verdict": analysis.risk_level,
            "suspicion_score": analysis.suspicion_score,
            "explanation": analysis.explanation_text,
            "recommendation": analysis.recommendation_text,
            "times_analyzed_before": resource.occurrence_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
