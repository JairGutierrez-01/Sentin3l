from tkinter.dnd import dnd_start

from sentin3l.database.session import SessionLocal
from sentin3l.models.observed_resource import ObservedResource

def test_create_observed_resource():
    db = SessionLocal()

    try :
        resource = ObservedResource(
            hostname="login.example.com",
            registrable_domain="example.com",
            normalized_url_hash="abc1234hash"
        )
        db.add(resource)
        db.commit()
        db.refresh(resource)

        saved_resource = (
            db.query(ObservedResource)
            .filter_by(id=resource.id)
            .first()
        )
        assert saved_resource is not None
        assert saved_resource.hostname == "login.example.com"
        assert saved_resource.normalized_url_hash == "abc1234hash"
        assert saved_resource.registrable_domain == "example.com"
        assert saved_resource.occurrence_count == 1

    finally:
        db.close()
