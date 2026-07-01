import os
import logging
from sqlalchemy.orm import Session
from sentin3l.models.monitored_brand import MonitoredBrand

logger = logging.getLogger(__name__)

def seed_brands_from_file(db: Session, filename: str = "top_brands.txt") -> None:
    """Reads a plain text file containing brand names and seeds them into the database.

    Leverages high-performance set operations to cross-reference the incoming file
    against existing records, executing a localized batch insertion exclusively for
    new elements while entirely skipping duplicates.

    Args:
        db (Session): The active SQLAlchemy database session context.
        filename (str): The name of the target file inside the data directory.
                        Defaults to "top_brands.txt".
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "..", "data", filename)

    if not os.path.exists(file_path):
        logger.warning(f"The targeted brand dictionary file was not found at: {file_path}")
        return

    # Read, strip white spaces, convert to lowercase, and isolate unique values using a set
    with open(file_path, "r", encoding="utf-8") as f:
        file_brands = {line.strip().lower() for line in f if line.strip()}

    # Fetch existing entries from the database to compute the sync difference
    existing_brands_tuples = db.query(MonitoredBrand.name).all()
    existing_brands = {b[0] for b in existing_brands_tuples}

    # Identify novel brands using highly efficient set subtraction
    brands_to_insert = file_brands - existing_brands

    if brands_to_insert:
        new_brand_objects = [MonitoredBrand(name=brand) for brand in brands_to_insert]
        db.add_all(new_brand_objects)
        db.commit()
        logger.info(f"{len(new_brand_objects)} new monitored brands were successfully inserted.")
    else:
        logger.info("The monitored brands catalog is already up to date. No actions taken.")


def get_active_brands(db: Session) -> list[str]:
    """Retrieves an explicit flat list of strings representing all active monitored brand names.

    This list feeds directly into the typosquatting and impersonation detection heuristics
    within the core security engine pipelines.

    Args:
        db (Session): The active SQLAlchemy database session context.

    Returns:
        list[str]: A list of active target brand names.
    """
    brands = db.query(MonitoredBrand.name).filter(MonitoredBrand.is_active == True).all()
    return [b.name for b in brands]