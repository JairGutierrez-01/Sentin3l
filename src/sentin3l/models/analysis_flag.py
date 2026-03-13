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
"""

# TODO: inherit from Base
# TODO: define __tablename__ = "analysis_flags"

# TODO: add primary key field
# Expected:
# - id
# - integer primary key

# TODO: add foreign key to Analysis
# Expected:
# - analysis_id
# - required field
# - links each flag record to one analysis

# TODO: decide how to represent the flag identity in MVP
# MVP options:
# - simple string field such as flag_code
# - future foreign key to FlagDefinition
#
# Recommendation for MVP:
# - start with a simple flag_code string
# - keep future FlagDefinition as an optional later improvement

# TODO: add flag_code field
# Expected:
# - simple string identifier
# - examples:
#   - IP_IN_HOST
#   - LONG_URL
#   - SUSPICIOUS_KEYWORD
#   - EXCESSIVE_SUBDOMAINS

# TODO: add weight_applied field
# Expected:
# - numerical value
# - represents how much this flag contributed to the final score
# - may start as integer in MVP

# TODO: decide whether evidence_summary belongs in MVP
# Possible field:
# - short text describing why the flag was triggered
# Example:
# - "Host uses a direct IP address"
# - "URL length exceeded configured threshold"
#
# This can be useful for transparency, but may remain optional in MVP.

# TODO: add relationship to Analysis later
# One analysis will likely have many AnalysisFlag records.

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