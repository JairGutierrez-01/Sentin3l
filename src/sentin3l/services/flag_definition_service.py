from sqlalchemy.orm import Session
from typing import Optional, List
from sentin3l.models.flag_definition import FlagDefinition
import json
import os



def get_flag_by_code(db: Session, code: str) -> Optional[FlagDefinition]:
    """
    Search for a rule by its unique code.
    Used to obtain the weight and technical description of a find.
    """
    return db.query(FlagDefinition).filter_by(code=code).first()

def get_all_active_flags(db: Session) -> List[FlagDefinition]:
    """
    Retrieves all active rules.
    Useful for loading the entire catalog into the interface or into memory.
    """
    return db.query(FlagDefinition).filter_by(is_active=True).all()


def seed_default_flags(db: Session):
    # 1. Buscamos el archivo JSON
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "..", "data", "default_flags.json")

    # 2. Leemos las reglas
    with open(file_path, "r", encoding="utf-8") as f:
        default_flags = json.load(f)

    # 3. Las insertamos
    for flag_data in default_flags:
        if not get_flag_by_code(db, flag_data["code"]):
            new_flag = FlagDefinition(**flag_data)
            db.add(new_flag)

    db.commit()