from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List
from datetime import datetime


class AnalysisFlagSchema(BaseModel):
    code: str
    evidence_summary: str
    name: Optional[str] = "Unknown Flag"
    description: Optional[str] = "Description not available yet."

    class Config:
        from_attributes = True

class AnalysisResponse(BaseModel):
    id: int
    target_url: str
    safe_url: str
    suspicion_score: int
    risk_level:str
    explanation_text: str
    recommendation_text: str
    times_analyzed_before: int
    analyzed_at: datetime
    flags: list[AnalysisFlagSchema] = []

    class config:
        from_attributes = True

