import json
import os
from sentin3l.services import flag_definition_service
from sentin3l.models.flag_definition import FlagDefinition


def get_expected_flag_count() -> int:
    """
    Auxiliary function that dynamically reads the JSON file
    to determine how many rules should be in the database.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, "..", "..", "src", "sentin3l", "data", "default_flags.json")

    with open(json_path, "r", encoding="utf-8") as f:
        return len(json.load(f))


def test_seed_default_flags(db_session):
    expected_count = get_expected_flag_count()

    flag_definition_service.seed_default_flags(db_session)

    flags = db_session.query(FlagDefinition).all()
    # Dynamic
    assert len(flags) == expected_count

    ip_flag = flag_definition_service.get_flag_by_code(db_session, "IP_IN_HOST")
    assert ip_flag is not None
    assert ip_flag.default_weight == 35


def test_seed_is_idempotent(db_session):
    expected_count = get_expected_flag_count()
    flag_definition_service.seed_default_flags(db_session)
    flag_definition_service.seed_default_flags(db_session)

    flags = db_session.query(FlagDefinition).all()
    assert len(flags) == expected_count


def test_get_all_active_flags(db_session):
    expected_count = get_expected_flag_count()

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
    assert len(active_flags) == expected_count

    total_flags = db_session.query(FlagDefinition).count()
    assert total_flags == expected_count + 1