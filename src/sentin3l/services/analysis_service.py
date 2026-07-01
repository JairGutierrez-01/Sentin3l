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
    """Loads the intelligence lists from the JSON file and keeps them in RAM.

    Utilizes an LRU cache with a maxsize of 1 to prevent redundant disk I/O operations
    across multiple analysis pipeline executions.

    Returns:
        dict: A dictionary containing security feeds such as suspicious TLDs,
              sensitive keywords, known URL shorteners, and dangerous extensions.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "..", "data", "threat_intel.json")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_security_detectors(
    raw_url: str,
    hostname: str,
    registrable_domain: str,
    target_brands: list[str]
) -> list[dict]:
    """Executes the complete sequence of security detection rules against a URL.

    Gathers results from all analytical detectors defined in the utils engine,
    filtering out negative results (None) and compiling active findings.

    Args:
        raw_url (str): The un-redacted target URL string to evaluate.
        hostname (str): The isolated network hostname of the target URL.
        registrable_domain (str): The root domain extracted from the host.
        target_brands (list[str]): List of highly targeted brand names for impersonation checks.

    Returns:
        list[dict]: A list of dictionary objects representing triggered threat indicators,
                    each containing a "code" and an "evidence" summary.
    """
    findings = []

    parsed_url = urlparse(raw_url)
    url_path = parsed_url.path

    intel = load_threat_intel()

    # Sequential pipeline execution of heuristic detectors
    pipeline = [
        # Core URL Structure Heuristics
        detectors.detect_ip_host(hostname),
        detectors.detect_long_url(raw_url),
        detectors.detect_suspicious_tld(registrable_domain, intel["suspicious_tlds"]),
        detectors.detect_sensitive_keywords(raw_url, intel["sensitive_keywords"]),
        detectors.detect_punycode(hostname),
        detectors.detect_excessive_subdomains(hostname),

        # Impersonation & Social Engineering Heuristics
        detectors.detect_typosquatting(registrable_domain, target_brands),
        detectors.detect_url_shortener(hostname, intel["url_shorteners"]),
        detectors.detect_brand_impersonation(hostname, registrable_domain, target_brands),

        # Obfuscation & Evasion Heuristics
        detectors.detect_at_symbol(raw_url),
        detectors.detect_double_extension(url_path, intel["dangerous_extensions"]),
        detectors.detect_insecure_protocol(raw_url)
    ]

    # Filter out inactive/None signals from the pipeline
    for result in pipeline:
        if result:
            findings.append(result)

    return findings


def calculate_risk_level(suspicion_score: int, total_flags: int) -> str:
    """Determines the categorical risk assessment based on the cumulative severity score.

    Args:
        suspicion_score (int): The aggregated weight score of all triggered flags.
        total_flags (int): The total count of triggered detection flags.

    Returns:
        str: A risk classification string label ("Safe", "Low", "Medium", or "High").
    """
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
    """Orchestrates and persists an analysis execution pipeline for an observed resource.

    Triggers all heuristic security tests, cross-references triggered findings with
    the database's centralized FlagDefinitions to apply proper scoring weights,
    maps cascading AnalysisFlags, and commits the state into the SQLite backend.

    Args:
        db (Session): The active SQLAlchemy database session context.
        resource (ObservedResource): The persistent metadata record of the target domain/URL.
        raw_url (str): The raw user-submitted input URL required by the specific heuristics.

    Returns:
        Analysis: The newly created, populated, and database-committed Analysis record.
    """
    target_brands = brand_service.get_active_brands(db)

    # Run the detection suite
    findings = run_security_detectors(
        raw_url,
        resource.hostname,
        resource.registrable_domain,
        target_brands
    )

    # Initialize the core Analysis Object structure
    new_analysis = Analysis(
        observed_resource_id=resource.id,
        analyzed_at=datetime.now(timezone.utc),
        suspicion_score=0,
        explanation_text="",
        recommendation_text="Look at the URL carefully before interacting."
    )

    explanations = []
    for finding in findings:
        # Retrieve the central configuration catalog data for weights and names
        flag_def = flag_definition_service.get_flag_by_code(db, finding["code"])

        if flag_def:
            weight = flag_def.default_weight
            new_analysis.suspicion_score += weight

            # Establish the contextual AnalysisFlag occurrence mapping
            analysis_flag = AnalysisFlag(
                flag_definition_id=flag_def.id,
                weight_applied=weight,
                evidence_summary=finding["evidence"]
            )
            # Append relationship to leverage SQLAlchemy cascade operations
            new_analysis.flags.append(analysis_flag)
            explanations.append(f"- {flag_def.name}: {finding['evidence']}")

    # Conclude metadata evaluations
    new_analysis.risk_level = calculate_risk_level(new_analysis.suspicion_score, len(findings))

    if not findings:
        new_analysis.explanation_text = "No known risk indicators were detected."
        new_analysis.recommendation_text = "This URL appears safe to browse."
    else:
        new_analysis.explanation_text = "\n".join(explanations)

    # Persistence handling
    db.add(new_analysis)
    db.commit()
    db.refresh(new_analysis)

    return new_analysis


def get_recent_analyses(db: Session, limit: int = 10) -> list[Analysis]:
    """Retrieves the latest analyses logs sorted chronologically for global activity feeds.

    Optimized using 'joinedload' to fetch the associated ObservedResource relation
    in a single, unified database query execution to eliminate N+1 latency behaviors.

    Args:
        db (Session): The active SQLAlchemy database session context.
        limit (int): The maximum count of analysis objects to retrieve. Defaults to 10.

    Returns:
        list[Analysis]: A list of populated Analysis records including eager-loaded resources.
    """
    return (
        db.query(Analysis)
        .order_by(Analysis.analyzed_at.desc())
        .limit(limit)
        .all()
    )