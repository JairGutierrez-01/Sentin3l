from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class AnalysisFlagSchema(BaseModel):
    """Schema representing an individual threat flag triggered during an analysis."""
    model_config = ConfigDict(from_attributes=True)

    code: str
    evidence_summary: str
    name: Optional[str] = "Unknown Flag"
    description: Optional[str] = "Description not available yet."


class AnalysisResponse(BaseModel):
    """Schema representing the complete, structured analysis payload returned to the frontend."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    target_url: str
    safe_url: str
    suspicion_score: int
    risk_level: str
    explanation_text: str
    recommendation_text: str
    times_analyzed_before: int
    analyzed_at: datetime
    flags: List[AnalysisFlagSchema] = []