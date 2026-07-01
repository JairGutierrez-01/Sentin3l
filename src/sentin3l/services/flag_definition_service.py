import os
import json
from typing import Optional, List
from sqlalchemy.orm import Session
from sentin3l.models.flag_definition import FlagDefinition

def get_flag_by_code(db: Session, code: str) -> Optional[FlagDefinition]:
    """Retrieves a specific flag definition from the database by its unique code string.

    This function is primarily used during the analysis pipeline to obtain
    the technical severity weight and full descriptive name of a triggered heuristic.

    Args:
        db (Session): The active SQLAlchemy database session context.
        code (str): The unique identifier string of the flag (e.g., 'IP_IN_HOST').

    Returns:
        Optional[FlagDefinition]: The matching FlagDefinition instance if found,
                                  otherwise None.
    """
    return db.query(FlagDefinition).filter_by(code=code).first()


def get_all_active_flags(db: Session) -> List[FlagDefinition]:
    """Retrieves all threat detection flags that are currently marked as active.

    Useful for loading the complete active rules catalog into the user interface,
    caching mechanisms, or validation engines.

    Args:
        db (Session): The active SQLAlchemy database session context.

    Returns:
        List[FlagDefinition]: A list of all active FlagDefinition records.
    """
    return db.query(FlagDefinition).filter_by(is_active=True).all()


def seed_default_flags(db: Session) -> None:
    """Seeds the database with default security flag definitions from a local JSON configuration.

    Parses the 'default_flags.json' file, validates whether each flag already exists
    by its unique code to prevent duplication, stages new entries, and commits
    the state transactionally.

    Args:
        db (Session): The active SQLAlchemy database session context.
    """
    # 1. Locate the default flags JSON file destination
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "..", "data", "default_flags.json")

    # 2. Read and parse the target rule definitions
    with open(file_path, "r", encoding="utf-8") as f:
        default_flags = json.load(f)

    # 3. Process and perform safe conditional insertions
    for flag_data in default_flags:
        if not get_flag_by_code(db, flag_data["code"]):
            new_flag = FlagDefinition(**flag_data)
            db.add(new_flag)

    db.commit()