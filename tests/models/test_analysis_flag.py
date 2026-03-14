import pytest
from sqlalchemy.exc import IntegrityError

from sentin3l.models.observed_resource import ObservedResource
from sentin3l.models.analysis import Analysis
from sentin3l.models.analysis_flag import AnalysisFlag
from sentin3l.models.flag_definition import FlagDefinition


def test_create_analysis_flag_success(db_session):
    definition = FlagDefinition(
        code = "SUSPICIOUS_KEYWORD",
        name = "Suspicious keyword in URL",
        description= "A keyword associated with phising was found in the URL.",
        default_weight= 20
    )
    db_session.add(definition)

    resource = ObservedResource(
        hostname="malicious-flag.com",
        registrable_domain="malicious-flag.com",
        normalized_url_hash="hash_flag_1"
    )
    db_session.add(resource)
    db_session.commit()
    db_session.refresh(resource)
    db_session.refresh(definition)

    analysis = Analysis(
        observed_resource_id=resource.id,
        suspicion_score=25,
        explanation_text="Test explanation.",
        recommendation_text="Test recommendation."
    )
    db_session.add(analysis)
    db_session.commit()
    db_session.refresh(analysis)

    flag = AnalysisFlag(
        analysis_id=analysis.id,
        flag_definition_id=definition.id,
        weight_applied=25,
        evidence_summary="Found keyword: 'login-update'"
    )
    db_session.add(flag)
    db_session.commit()
    db_session.refresh(flag)

    assert flag.id is not None
    assert flag.definition.code == "SUSPICIOUS_KEYWORD"
    assert flag.weight_applied == 25
    assert flag.evidence_summary == "Found keyword: 'login-update'"


def test_analysis_flag_defaults(db_session):

    definition = FlagDefinition(
        code="LONG_URL",
        name="URL is too long",
        description="The URL exceeds the normal character limit."
    )
    db_session.add(definition)

    # 2. Crear Recurso
    resource = ObservedResource(
        hostname="neutral-flag.com",
        registrable_domain="neutral-flag.com",
        normalized_url_hash="hash_flag_2"
    )
    db_session.add(resource)
    db_session.commit()
    db_session.refresh(resource)
    db_session.refresh(definition)

    analysis = Analysis(
        observed_resource_id=resource.id,
        explanation_text="Default flag test.",
        recommendation_text="Default flag test."
    )
    db_session.add(analysis)
    db_session.commit()
    db_session.refresh(analysis)

    flag = AnalysisFlag(
        analysis_id=analysis.id,
        flag_definition_id=definition.id,
        evidence_summary="URL exceeds 100 characters."
    )
    db_session.add(flag)
    db_session.commit()
    db_session.refresh(flag)

    assert flag.weight_applied == 0
    assert flag.evidence_summary == "URL exceeds 100 characters."


def test_analysis_can_have_multiple_flags(db_session):

    resource = ObservedResource(
        hostname="multi-flag.com",
        registrable_domain="multi-flag.com",
        normalized_url_hash="hash_flag_3"
    )
    db_session.add(resource)
    db_session.commit()
    db_session.refresh(resource)

    analysis = Analysis(
        observed_resource_id=resource.id,
        explanation_text="Multiple flags test.",
        recommendation_text="Multiple flags test."
    )
    db_session.add(analysis)

    def_ip = FlagDefinition(code="IP_IN_HOST", name="IP in Host", description= "IP used instead of domain")
    def_sub = FlagDefinition(code="EXCESSIVE_SUBDOMAINS", name="Too many subdomains", description= "Suspicious subdomain count")
    db_session.add_all([def_ip, def_sub])

    db_session.commit()
    db_session.refresh(analysis)
    db_session.refresh(def_ip)
    db_session.refresh(def_sub)

    flag1 = AnalysisFlag(
        analysis_id=analysis.id,
        flag_definition_id=def_ip.id,
        weight_applied=40,
        evidence_summary="Found IP: 192.168.1.1"
    )

    flag2 = AnalysisFlag(
        analysis_id=analysis.id,
        flag_definition_id=def_sub.id,
        weight_applied=20,
        evidence_summary="Found EXCESSIVE_SUBDOMAINS: 192.168.1.1"
    )
    db_session.add_all([flag1, flag2])
    db_session.commit()

    assert len(analysis.flags) == 2

    flag_codes = [f.definition.code for f in analysis.flags]
    assert "IP_IN_HOST" in flag_codes
    assert "EXCESSIVE_SUBDOMAINS" in flag_codes


def test_analysis_flag_requires_analysis_id(db_session):
    definition = FlagDefinition(code="ORPHAN_FLAG", name="Orphan", description="Orphan definition test")
    db_session.add(definition)
    db_session.commit()
    db_session.refresh(definition)


    flag = AnalysisFlag(
        flag_definition_id=definition.id,
        weight_applied=10,
        evidence_summary="Missing analysis ID test"
    )
    db_session.add(flag)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_analysis_flag_requires_definition_id(db_session):
    flag = AnalysisFlag(
        analysis_id=1,  # Fake ID
        flag_definition_id=999,  # Fake ID
        weight_applied=10,
        evidence_summary="This should fail"
    )
    db_session.add(flag)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()