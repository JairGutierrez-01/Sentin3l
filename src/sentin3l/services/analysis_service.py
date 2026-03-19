from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sentin3l.models.analysis import Analysis
from sentin3l.models.analysis_flag import AnalysisFlag
from sentin3l.models.observed_resource import ObservedResource
from sentin3l.services import flag_definition_service
from sentin3l.utils import detectors


def run_security_detectors(raw_url: str, hostname: str, registrable_domain: str) -> list[dict]:
    findings = []

    pipeline = [
        detectors.detect_ip_host(hostname),
        detectors.detect_long_url(raw_url),
        detectors.detect_suspicious_tld(registrable_domain),
        detectors.detect_sensitive_keywords(raw_url),
        detectors.detect_punycode(hostname),
        detectors.detect_excessive_subdomains(hostname)
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
    # Run detectors
    findings = run_security_detectors(
        raw_url,
        resource.hostname,
        resource.registrable_domain
    )

    # Initialize the Analysis Object
    new_analysis = Analysis(
        observed_resource_id=resource.id,
        analyzed_at=datetime.now(timezone.utc),
        suspicion_score=0,
        explanation_text="",
        recommendation_text="Observe la URL con cuidado antes de interactuar."
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
        new_analysis.explanation_text = "No se detectaron indicadores de riesgo conocidos."
        new_analysis.recommendation_text = "Esta URL parece segura para navegar."
    else:
        new_analysis.explanation_text = "\n".join(explanations)

    # 5. Persistence
    db.add(new_analysis)
    db.commit()
    db.refresh(new_analysis)

    return new_analysis