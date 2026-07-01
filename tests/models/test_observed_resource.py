from sqlalchemy.orm import Session
from sentin3l.models.observed_resource import ObservedResource


def test_create_observed_resource(db_session: Session):
    """
    Verifies that an ObservedResource can be successfully persisted
    using an isolated test database session.
    """
    resource = ObservedResource(
        hostname="login.example.com",
        registrable_domain="example.com",
        normalized_url_hash="abc1234hash"
    )

    # Using the db_session fixture guarantees this rolls back after the test completes
    db_session.add(resource)
    db_session.commit()
    db_session.refresh(resource)

    saved_resource = (
        db_session.query(ObservedResource)
        .filter_by(id=resource.id)
        .first()
    )

    assert saved_resource is not None
    assert saved_resource.hostname == "login.example.com"
    assert saved_resource.normalized_url_hash == "abc1234hash"
    assert saved_resource.registrable_domain == "example.com"
    assert saved_resource.occurrence_count == 1