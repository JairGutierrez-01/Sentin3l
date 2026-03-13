from sentin3l.database.session import Base, engine
from sentin3l.models.observed_resource import ObservedResource

def init_db() -> None:
    Base.metadata.create_all(engine)