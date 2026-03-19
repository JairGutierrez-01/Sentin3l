from sqlalchemy import Column, Integer, String, Boolean
from sentin3l.database.session import Base

class MonitoredBrand(Base):
    __tablename__ = 'monitored_brand'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
