"""
ObservedResource service layer.

Purpose:
    Handle business logic related to the ObservedResource entity.

Why this service exists:
    The model defines how ObservedResource is stored in the database.
    This service defines how ObservedResource should behave in the application.

Current MVP role:
    - Register a newly observed resource
    - Detect whether a resource was already seen before
    - Update occurrence tracking metadata
    - Keep persistence logic separated from API routes

Out of scope for now:
    - Full URL normalization pipeline
    - URL hashing implementation
    - Analysis creation
    - Suspicion scoring
    - Explanation generation
    - Credential leak logic

Related entities:
    - ObservedResource
    - Analysis (future)
    - AnalysisFlag (future)

Related future modules:
    - URL parser / normalization utilities
    - Analysis service
    - Scoring service
    - Explanation service
"""

from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional

from sentin3l.models.observed_resource import ObservedResource
from sentin3l.utils.url_tools import process_url_for_storage


def get_resource_by_hash(
        db: Session,
        normalized_url_hash: str,
) -> Optional[ObservedResource]:

    return db.query(ObservedResource).filter(
        ObservedResource.normalized_url_hash == normalized_url_hash
    ).first()


def create_resource(
        db: Session,
        normalized_url_hash: str,
        hostname: str,
        registrable_domain: str
) -> ObservedResource:

    resource = ObservedResource(
        normalized_url_hash=normalized_url_hash,
        hostname=hostname,
        registrable_domain=registrable_domain
    )
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return resource


def update_occurrence(db: Session, resource: ObservedResource) -> ObservedResource:

    resource.occurrence_count += 1
    resource.last_seen_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(resource)
    return resource


def get_or_create_resource(
        db: Session,
        raw_url:str,
) -> ObservedResource:

    # privacy filter
    url_data = process_url_for_storage(raw_url)
    # threat already seen?
    resource = get_resource_by_hash(db, url_data['normalized_url_hash'])

    if resource:
        return update_occurrence(db, resource)
    else:
        return create_resource(
            db = db,
            normalized_url_hash=url_data['normalized_url_hash'],
            hostname=url_data['hostname'],
            registrable_domain=url_data['registrable_domain']
        )

# -----------------------------------------------------------------------------
# Design notes
# -----------------------------------------------------------------------------

# TODO: decide the stable lookup strategy for ObservedResource
# Options may include:
# - normalized_url_hash
# - hostname + registrable_domain
# - future composite logic

# TODO: keep privacy-conscious storage in mind
# The service should avoid introducing storage of:
# - raw credentials
# - sensitive secrets
# - unnecessary personal data

# TODO: keep service logic separate from API routes
# Routes should call this service instead of embedding DB logic directly.

# TODO: keep service logic separate from the model
# The model defines persistence structure.
# The service defines application behavior.

# -----------------------------------------------------------------------------
# Future extension points
# -----------------------------------------------------------------------------

# TODO: support repeated occurrence statistics
# TODO: support future domain exposure or leak-related modules carefully