import os
import logging
from sqlalchemy.orm import Session
from sentin3l.models.monitored_brand import MonitoredBrand

logger = logging.getLogger(__name__)


def seed_brands_from_file(db: Session, filename: str = "top_brands.txt"):
    """
    Reads a text file with marks and inserts them into the database,
    ignoring those that already exist.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "..", "data", filename)

    if not os.path.exists(file_path):
        logger.warning(f"The markup file was not found in {file_path}")
        return

    # Read and clean the file
    with open(file_path, "r", encoding="utf-8") as f:
        # line.strip() quita espacios y saltos de línea
        file_brands = {line.strip().lower() for line in f if line.strip()}

    #
    existing_brands_tuples = db.query(MonitoredBrand.name).all()
    existing_brands = {b[0] for b in existing_brands_tuples}

    # find only the new brands
    brands_to_insert = file_brands - existing_brands

    if brands_to_insert:

        new_brand_objects = [MonitoredBrand(name=brand) for brand in brands_to_insert]

        db.add_all(new_brand_objects)
        db.commit()
        logger.info(f"{len(new_brand_objects)} new monitored brands were inserted.")
    else:
        logger.info("The list of brands has already been updated. Nothing new has been added.")


def get_active_brands(db: Session) -> list[str]:
    """
    Returns a list of strings with the active tags to use in the detectors.
    """
    brands = db.query(MonitoredBrand.name).filter(MonitoredBrand.is_active == True).all()
    return [b.name for b in brands]