from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone

from sqlalchemy.orm import relationship

from sentin3l.database.session import Base


class ObservedResource(Base):
    __tablename__ = "observed_resources"

    id = Column(Integer, primary_key=True, index=True)
    hostname = Column(String, nullable=False, index=True)
    registrable_domain = Column(String, nullable=False, index=True)
    normalized_url_hash = Column(String, nullable=False, unique=True)
    first_seen_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    last_seen_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    occurrence_count = Column(Integer, default=1)  # have to check this

    #Relations
    analyses = relationship("Analysis", back_populates="resource", cascade="all, delete-orphan")

# Still have to decide if  normalized_url_hash is gonna be unique or not.
# decide if there is gonna be composite constraint to avoid duplicates in hostname/domain
# decidie if is convenient to save some additional hash for the path
# maybe add more relations with analysis
