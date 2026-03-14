from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Text, Boolean

from sentin3l.database.session import Base

class FlagDefinition(Base):
    __tablename__ = "flag_definitions"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    default_weight = Column(Integer,nullable = False, default= 0)
    is_active = Column(Boolean, nullable=False, default=True)

    #Relations
    flags = relationship("AnalysisFlag", back_populates="definition")

