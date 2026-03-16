from sentin3l.services.observed_resource_service import (
    get_or_create_resource,
    get_resource_by_hash,
    create_resource,
    update_occurrence
)
from sentin3l.models.observed_resource import ObservedResource

def test_create_resource_direct(db_session):

    fake_hash = "atomic-hash-1"
    resource = create_resource(db_session, fake_hash, "host1.com", "domain1.com")

    assert resource.id is not None
    assert resource.normalized_url_hash == fake_hash
    assert resource.occurrence_count == 1


def test_update_occurrence_direct(db_session):

    resource = create_resource(db_session, "atomic-hash-2", "host2.com", "domain2.com")
    updated_resource = update_occurrence(db_session, resource)

    assert updated_resource.occurrence_count == 2
    assert updated_resource.last_seen_at is not None

def test_get_or_create_resource_when_new(db_session):

    fake_hash = "abc123hash"

    resource = get_or_create_resource(
        db=db_session,
        normalized_url_hash=fake_hash,
        hostname="login.fake-bank.com",
        registrable_domain="example.com"
    )

    assert resource.id is not None
    assert resource.normalized_url_hash == fake_hash
    assert resource.occurrence_count == 1


def test_get_or_create_resource_when_existing(db_session):

    fake_hash = "abc123hash-existing"
    fake_host = "login.fake-bank.com"
    fake_domain = "example.com"


    get_or_create_resource(db_session, fake_hash, fake_host, fake_domain)


    resource_updated = get_or_create_resource(db_session, fake_hash, fake_host, fake_domain)

    total_records = db_session.query(ObservedResource).filter_by(normalized_url_hash=fake_hash).count()
    assert total_records == 1
    assert resource_updated.occurrence_count == 2


def test_get_resource_by_hash_found(db_session):
    fake_hash = "hash to find-123"
    create_resource(db_session, fake_hash, "test.com", "test.com")

    found_resource = get_resource_by_hash(db=db_session, normalized_url_hash=fake_hash)

    assert found_resource is not None
    assert found_resource.normalized_url_hash == fake_hash


def test_get_resource_by_hash_not_found(db_session):
    invented_hash = "Ghost hash"
    found_resource = get_resource_by_hash(db=db_session, normalized_url_hash=invented_hash)
    assert found_resource is None

