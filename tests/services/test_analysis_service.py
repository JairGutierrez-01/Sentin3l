from sentin3l.services import analysis_service, flag_definition_service
from sentin3l.models.observed_resource import ObservedResource


def test_calculate_risk_level():
    assert analysis_service.calculate_risk_level(suspicion_score=0, total_flags=0) == "Safe"
    assert analysis_service.calculate_risk_level(suspicion_score=15, total_flags=1) == "Low"
    assert analysis_service.calculate_risk_level(suspicion_score=45, total_flags=2) == "Medium"
    assert analysis_service.calculate_risk_level(suspicion_score=80, total_flags=3) == "High"


def test_create_analysis_safe_url(db_session):
    resource = ObservedResource(
        normalized_url_hash="hash_seguro",
        hostname="google.com",
        registrable_domain="google.com"
    )
    db_session.add(resource)
    db_session.commit()

    safe_url = "https://google.com/search"
    analysis = analysis_service.create_analysis_for_resource(db_session, resource, raw_url=safe_url)

    assert analysis.suspicion_score == 0
    assert analysis.risk_level == "Safe"
    assert len(analysis.flags) == 0
    assert "segura" in analysis.recommendation_text.lower()


def test_create_analysis_malicious_url(db_session):
    flag_definition_service.seed_default_flags(db_session)

    resource = ObservedResource(
        normalized_url_hash="hash_malicioso",
        hostname="192.168.1.100",  # (35 pts)
        registrable_domain="192.168.1.100"
    )
    db_session.add(resource)
    db_session.commit()

    # (40 pts)
    bad_url = "https://192.168.1.100/login/update"
    analysis = analysis_service.create_analysis_for_resource(db_session, resource, bad_url)

    # ( 75 puntos)
    assert analysis.suspicion_score == 75
    assert analysis.risk_level == "High"

    assert len(analysis.flags) == 2

    assert "IP_IN_HOST" in analysis.explanation_text or "IP" in analysis.explanation_text