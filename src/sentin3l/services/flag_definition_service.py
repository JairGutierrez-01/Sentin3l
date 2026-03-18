from sqlalchemy.orm import Session
from typing import Optional, List
from sentin3l.models.flag_definition import FlagDefinition

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
    default_flags = [
        {
            "code": "IP_IN_HOST",
            "name": "IP Address in Host",
            "default_weight": 35,
            "description": "The use of IP addresses is common to hide the server's identity and evade filters."
        },
        {
            "code": "LONG_URL",
            "name": "URL is excessively long",
            "default_weight": 15,
            "description": "Extremely long URLs can hide malicious parameters or confuse the user."
        },
        {
            "code": "SUSPICIOUS_TLD",
            "name": "Risk domain extension",
            "default_weight": 25,
            "description": "The domain uses an extension (.zip, .tk) frequently used for phishing attacks."
        },
        {
            "code": "SENSITIVE_KEYWORDS",
            "name": "Social engineering keywords",
            "default_weight": 40,
            "description": "Terms such as 'login', 'verify' or 'secure' were detected in a suspicious URL structure, indicating a possible attempt at deception."
        }
    ]

    for flag_data in default_flags:
        if not get_flag_by_code(db, flag_data["code"]):
            new_flag = FlagDefinition(**flag_data)
            db.add(new_flag)

    db.commit()