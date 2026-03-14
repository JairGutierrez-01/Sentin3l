"""
AnalysisFlag model.

Purpose:
    Represent one indicator or flag detected during a specific analysis.

Current MVP role:
    Store the concrete detection signals that contributed to an Analysis result.

Main responsibilities:
    - link a detected flag to one Analysis
    - store the flag identity or code
    - store the applied weight if needed
    - optionally store short evidence or context

Out of scope for now:
    - detection logic itself
    - scoring logic itself
    - explanation generation
    - advanced evidence storage
    - full rule catalog design

maybe in the future (truly important but not for the beginning)
    - FlagDefinition
    - AnalysisFlag.flag_definition_id

conceptual relation: Analysis 1 ─── N AnalysisFlag
remember to use constants for the string like "FLAG_LONG_URL = "LONG_URL"
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship

from sentin3l.database.session import Base

class AnalysisFlag(Base):
    __tablename__ = "analysis_flag"

    id = Column(Integer, primary_key=True, index=True)

    analysis_id = Column (
        Integer,
        ForeignKey("analyses.id", ondelete="CASCADE"),
        nullable=False
    )

    flag_definition_id = Column (
        Integer,
        ForeignKey("flag_definitions.id"),
        nullable=False
    )

    #detection details - how much this flags affects the score -
    weight_applied = Column(Integer, nullable=False, default= 0 )

    #evidence like : if the flag is SUSPICIOUS_KEYWORD then evidence could be like "login"
    evidence_summary = Column(String, nullable=False)

    #Relations
    analysis = relationship("Analysis", back_populates="flags")
    definition = relationship("FlagDefinition", back_populates="flags")


# -----------------------------------------------------------------------------
# MVP notes
# -----------------------------------------------------------------------------

# TODO: keep this model simple and explainable
# Avoid overengineering a full rule catalog too early.

# TODO: do not place detection logic inside the model
# Detection belongs to services or rule-processing modules.

# TODO: support explainability
# This model should help explain why an Analysis produced a given score.

# -----------------------------------------------------------------------------
# Future notes
# -----------------------------------------------------------------------------

# TODO: consider introducing FlagDefinition as a separate catalog entity later
# That future entity could standardize:
# - code
# - label
# - default weight
# - description

# TODO: consider storing richer evidence later
# For example:
# - threshold values
# - matched keyword
# - matched pattern fragment

# TODO: consider version-aware flag generation later
# Useful if detection rules evolve over time.