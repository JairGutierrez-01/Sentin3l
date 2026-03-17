from sqlalchemy.orm import Session
from sentin3l.models.observed_resource import ObservedResource
from sentin3l.models.analysis import Analysis
from sentin3l.models.analysis_flag import AnalysisFlag


def _run_security_detectors(safe_url: str, hostname: str) -> list[dict]:
    """
    ATTENTION: There is NO database here. Pure cybersecurity logic.

    This internal function will take the clean URL and pass it through our future
    detection utilities (e.g. check length, search for keywords, etc.).

    Returns a list with the evidence found.
    Return example: [{"code": "KEYWORD_MATCH", "evidence": "found 'login' in path"}]
    """
    pass  # TODO: Create detectors in a different file (ej. utils/detectors.py)

def _calculate_risk_level(suspicion_score: int) -> str:
    """
    Converts a numerical score to a label.
    Ex: 0-20 = 'Low', 21-50 = 'Medium', 51-100 = 'High'.
    """
    pass # TODO: Define the risk


def create_analysis_for_resource(
        db: Session,
        resource: ObservedResource,
        safe_url: str
) -> Analysis:
    """
    The main of the Verdict.

    Expected Workflow:
    1. Call _run_security_detectors(safe_url) to get threats.
    2. For each threat, look for its FlagDefinition in the DB.
    3. Create AnalysisFlag instances (relating the Analysis and the FlagDefinition).
    4. Add the weights of the flags to calculate the final suspicion_score.
    5. Call _calculate_risk_level() for the risk_level.
    6. Generate an explanation_text based on the flags found.
    7. Save the Analysis object (and its cascading flags) to the database.
    8. Return the Analysis ready.
    """
    pass  # TODO: Implement the main 4 model idea here