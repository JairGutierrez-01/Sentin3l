"""
Analysis model.

Purpose:
    Represent a single execution of the Sentin3l analysis pipeline
    for one observed resource.

Current MVP role:
    Store the final result of an analysis in a persistent and explainable way.

Main responsibilities:
    - link an analysis to one ObservedResource
    - store the suspicion score
    - store the risk classification
    - store the explanation shown to the user
    - store the recommendation shown to the user
    - record when the analysis happened

Out of scope for now: (3-03-2026)
    - scoring logic itself
    - explanation generation logic
    - recommendation generation logic
    - advanced detector versioning
    - external intelligence enrichment

Not to forget: ObservedResource 1 ─── N Analysis
"""

from sqlalchemy.orm import relationship
from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, Text
from datetime import datetime, timezone

from sentin3l.database.session import Base

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    observed_resource_id = Column(Integer, ForeignKey("observed_resources.id", ondelete="CASCADE"), nullable=False)
    analyzed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    suspicion_score = Column(Integer, default=0, nullable=False)
    risk_level = Column(String, nullable=False, default="Low")

    explanation_text = Column(Text, nullable=False)
    recommendation_text = Column(Text, nullable=False)

    #Relations
    resource = relationship("ObservedResource", back_populates="analyses")
    flags = relationship("AnalysisFlag", back_populates="analysis", cascade="all, delete-orphan")
# -----------------------------------------------------------------------------
# MVP notes
# -----------------------------------------------------------------------------

# TODO: keep this model focused on persisted results
# Do not place scoring logic inside the model.

# TODO: keep explanation and recommendation as stored outputs
# Their generation belongs to services, not to the model.

# TODO: keep privacy-conscious storage
# Do not store credentials, personal identity data, or raw secrets.

# -----------------------------------------------------------------------------
# Future notes
# -----------------------------------------------------------------------------

# TODO: consider storing structured score breakdown later
# TODO: consider adding confidence score later
# TODO: consider adding analysis source metadata later