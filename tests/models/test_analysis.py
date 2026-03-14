import pytest
from sqlalchemy.exc import IntegrityError
from sentin3l.models.analysis import Analysis
from sentin3l.models.observed_resource import ObservedResource

def test_create_analysis_success(db_session):
    resource = ObservedResource(
        hostname="malicious.example.com",
        registrable_domain="example.com",
        normalized_url_hash="hash_success_123"
    )
    db_session.add(resource)
    db_session.commit()
    db_session.refresh(resource)

    analysis = Analysis(
        observed_resource_id=resource.id,
        suspicion_score=45,
        risk_level="Medium",
        explanation_text="This resource shows suspicious patterns.",
        recommendation_text="Avoid interacting with it until verified."
    )
    db_session.add(analysis)
    db_session.commit()
    db_session.refresh(analysis)

    assert analysis.id is not None
    assert analysis.observed_resource_id == resource.id
    assert analysis.suspicion_score == 45
    assert analysis.risk_level == "Medium"
    assert analysis.explanation_text == "This resource shows suspicious patterns."
    assert analysis.recommendation_text == "Avoid interacting with it until verified."
    assert analysis.analyzed_at is not None

def test_analysis_defaults_are_applied(db_session):
    resource = ObservedResource(
        hostname="neutral.example.com",
        registrable_domain="example.com",
        normalized_url_hash="hash_defaults_456"
    )
    db_session.add(resource)
    db_session.commit()
    db_session.refresh(resource)

    analysis = Analysis(
        observed_resource_id=resource.id,
        explanation_text="Default test explanation.",
        recommendation_text="Default test recommendation."
    )
    db_session.add(analysis)
    db_session.commit()
    db_session.refresh(analysis)

    assert analysis.suspicion_score == 0
    assert analysis.risk_level == "Low"
    assert analysis.analyzed_at is not None

def test_analysis_relationship_to_resource(db_session):
    resource = ObservedResource(
        hostname="phishing.example.com",
        registrable_domain="example.com",
        normalized_url_hash="hash_relation_789"
    )
    db_session.add(resource)
    db_session.commit()
    db_session.refresh(resource)

    analysis = Analysis(
        resource=resource,
        suspicion_score=80,
        risk_level="High",
        explanation_text="Test explanation for relation.",
        recommendation_text="Test recommendation for relation."
    )
    db_session.add(analysis)
    db_session.commit()
    db_session.refresh(analysis)

    assert analysis.resource.id == resource.id
    assert analysis.resource.hostname == "phishing.example.com"

def test_analysis_requires_observed_resource_id(db_session):
    analysis = Analysis(
        suspicion_score=30,
        risk_level="Low",
        explanation_text="Missing FK test.",
        recommendation_text="Should fail."
    )
    db_session.add(analysis)

    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

def test_analysis_requires_explanation_text(db_session):
    resource = ObservedResource(
        hostname="test.com",
        registrable_domain="test.com",
        normalized_url_hash="hash_missing_expl_000"
    )
    db_session.add(resource)
    db_session.commit()
    db_session.refresh(resource)

    analysis = Analysis(
        observed_resource_id=resource.id,
        suspicion_score=20,
        risk_level="Low",
        recommendation_text="Should fail because explanation is missing."
    )
    db_session.add(analysis)

    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()