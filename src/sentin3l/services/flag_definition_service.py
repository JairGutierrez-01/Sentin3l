from sqlalchemy.orm import Session
from typing import Optional, List
from sentin3l.models.flag_definition import FlagDefinition

def get_flag_by_code(db: Session, code: str) -> Optional[FlagDefinition]:
    """
    Look up for a detection rule for ist unique code  (example: 'SUSPICIOUS_TLD')
    when analysis detects something weird in the URL,
    it will use this function to know how many score points should it give
    """
    pass # TODO: implement query (query.filter_by(code=code))

def get_all_active_flags(db: Session) -> List[FlagDefinition]:

    """
    Obtains all the rules of detection that are active
    it exist to load the rules in memory or to show them in the interface
    without using obsolete rules.
    """
    pass # TODO implement query (query.filter_by(is_active=True))