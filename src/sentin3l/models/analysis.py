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

# TODO: inherit from Base
# TODO: define __tablename__ = "analyses"

# TODO: add primary key field
# Expected:
# - id
# - integer primary key
# - indexed if useful

# TODO: add foreign key to ObservedResource
# Expected:
# - observed_resource_id
# - required field
# - links one analysis to one observed resource

# TODO: add analysis timestamp
# Expected:
# - analyzed_at
# - UTC-aware datetime
# - required field
# - default current UTC time

# TODO: add suspicion score field
# Expected:
# - numerical value
# - MVP can start with integer
# - exact scoring strategy may evolve later

# TODO: add risk level field
# Expected:
# - simple text classification
# - examples: low / medium / high
# - keep simple in MVP

# TODO: add explanation field
# Expected:
# - human-readable text
# - explains why the URL may be suspicious
# - required for explainability in MVP

# TODO: add recommendation field
# Expected:
# - plain-language user guidance
# - examples:
#   - proceed with caution
#   - avoid opening the link
#   - verify the sender

# TODO: decide whether detector_version belongs in MVP or later
# Possible future field:
# - detector_version
# This may help if scoring logic changes over time,
# but it is not required in the first implementation.

# TODO: add relationship to ObservedResource later
# This can be added once multiple models are connected cleanly.

# TODO: add relationship to AnalysisFlag later
# One analysis will likely have many AnalysisFlag records.

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
# TODO: consider storing model or detector version later
# TODO: consider adding confidence score later
# TODO: consider adding analysis source metadata later