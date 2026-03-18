from sentin3l.services import flag_definition_service
from sentin3l.models.flag_definition import FlagDefinition


def test_seed_default_flags(db_session):
    flag_definition_service.seed_default_flags(db_session)

    flags = db_session.query(FlagDefinition).all()
    assert len(flags) == 4

    ip_flag = flag_definition_service.get_flag_by_code(db_session, "IP_IN_HOST")
    assert ip_flag is not None
    assert ip_flag.default_weight == 35


def test_seed_is_idempotent(db_session):

    flag_definition_service.seed_default_flags(db_session)
    flag_definition_service.seed_default_flags(db_session)

    flags = db_session.query(FlagDefinition).all()
    assert len(flags) == 4


def test_get_all_active_flags(db_session):

    flag_definition_service.seed_default_flags(db_session)


    inactive_flag = FlagDefinition(
        code="OLD_RULE",
        name="Obsolete rule",
        description="This rule was giving false positives, so we turned it off.",
        default_weight=10,
        is_active=False
    )
    db_session.add(inactive_flag)
    db_session.commit()

    active_flags = flag_definition_service.get_all_active_flags(db_session)
    assert len(active_flags) == 4

    total_flags = db_session.query(FlagDefinition).count()
    assert total_flags == 5