from datetime import datetime, timezone
from sqlalchemy.orm import Session, joinedload
from sentin3l.models.analysis import Analysis
from sentin3l.models.analysis_flag import AnalysisFlag
from sentin3l.models.observed_resource import ObservedResource
from sentin3l.services import flag_definition_service
from sentin3l.utils import detectors
from sentin3l.services import brand_service
import json
import os
from functools import lru_cache
from urllib.parse import urlparse

@lru_cache(maxsize=1)
def load_threat_intel() -> dict:
    """It loads the intelligence lists from the JSON and keeps them in RAM."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "..", "data", "threat_intel.json")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def run_security_detectors(raw_url: str, hostname: str, registrable_domain: str, target_brands: list[str]) -> list[dict]:
    findings = []

    parsed_url = urlparse(raw_url)
    url_path = parsed_url.path

    intel = load_threat_intel()

    pipeline = [
        # OGs
        detectors.detect_ip_host(hostname),
        detectors.detect_long_url(raw_url),
        detectors.detect_suspicious_tld(registrable_domain, intel["suspicious_tlds"]),
        detectors.detect_sensitive_keywords(raw_url, intel["sensitive_keywords"]),
        detectors.detect_punycode(hostname),
        detectors.detect_excessive_subdomains(hostname),

        #suplatnation
        detectors.detect_typosquatting(registrable_domain, target_brands),
        detectors.detect_url_shortener(hostname, intel["url_shorteners"]),
        detectors.detect_brand_impersonation(hostname, registrable_domain, target_brands),

        # Evil
        detectors.detect_at_symbol(raw_url),
        detectors.detect_double_extension(url_path, intel["dangerous_extensions"]),
        detectors.detect_insecure_protocol(raw_url)
    ]

    for result in pipeline:
        if result:
            findings.append(result)

    return findings

def calculate_risk_level(suspicion_score: int, total_flags: int) -> str:
    """Determine the risk label based on the cumulative score."""
    if total_flags == 0:
        return "Safe"
    if suspicion_score <= 20:
        return "Low"
    if suspicion_score <= 55:
        return "Medium"
    return "High"


def create_analysis_for_resource(
        db: Session,
        resource: ObservedResource,
        raw_url: str
) -> Analysis:

    target_brands = brand_service.get_active_brands(db)

    # Run detectors
    findings = run_security_detectors(
        raw_url,
        resource.hostname,
        resource.registrable_domain,
        target_brands
    )

    # Initialize the Analysis Object
    new_analysis = Analysis(
        observed_resource_id=resource.id,
        analyzed_at=datetime.now(timezone.utc),
        suspicion_score=0,
        explanation_text="",
        recommendation_text="Look at the URL carefully before interacting."
    )

    # Process each thing found
    explanations = []
    for finding in findings:
        # Look up the definition of the flag in the database to obtain its weight.
        flag_def = flag_definition_service.get_flag_by_code(db, finding["code"])

        if flag_def:
            weight = flag_def.default_weight
            new_analysis.suspicion_score += weight

            # Create the AnalysisFlag relationship (Data Cross referencing)
            analysis_flag = AnalysisFlag(
                flag_definition_id=flag_def.id,
                weight_applied=weight,
                evidence_summary=finding["evidence"]
            )
            # Link the flag to the analysis (SQLAlchemy saves it in cascade)
            new_analysis.flags.append(analysis_flag)
            explanations.append(f"- {flag_def.name}: {finding['evidence']}")

    # Finalize verdict metadata
    new_analysis.risk_level = calculate_risk_level(new_analysis.suspicion_score, len(findings))

    if not findings:
        new_analysis.explanation_text = "No known risk indicators were detected."
        new_analysis.recommendation_text = "This URL appears safe to browse."
    else:
        new_analysis.explanation_text = "\n".join(explanations)

    # 5. Persistence
    db.add(new_analysis)
    db.commit()
    db.refresh(new_analysis)

    return new_analysis

def get_recent_analyses(db: Session, limit: int = 10):
    """"
    Retrieves the latest analyses performed to display them in the global feed.
    Uses 'joinedload' to retrieve the information from ObservedResource in a single query.
    """
    return (
        db.query(Analysis)
        .options(joinedload(Analysis.resource)) # Carga la relación ObservedResource
        .order_by(Analysis.analyzed_at.desc())
        .limit(limit)
        .all()
    )