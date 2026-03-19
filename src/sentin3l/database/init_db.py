import logging
from sentin3l.database.session import Base, engine, SessionLocal
from sentin3l.models.observed_resource import ObservedResource
from sentin3l.models.analysis import Analysis
from sentin3l.models.analysis_flag import AnalysisFlag
from sentin3l.models.flag_definition import FlagDefinition
from sentin3l.models.monitored_brand import MonitoredBrand

from sentin3l.services import flag_definition_service, brand_service

logger = logging.getLogger(__name__)


def init_db() -> None:

    Base.metadata.create_all(engine)

    db = SessionLocal()
    try:
        flag_definition_service.seed_default_flags(db)
        brand_service.seed_brands_from_file(db, "top_brands.txt")

    except Exception as e:
        logger.error(f"Error at seed_brands_from_file: {e}")
    finally:
        db.close()