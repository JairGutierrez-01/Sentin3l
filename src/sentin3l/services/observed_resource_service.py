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

# TODO: import required database session dependencies
# TODO: import ObservedResource model

# -----------------------------------------------------------------------------
# MVP responsibilities
# -----------------------------------------------------------------------------

# TODO: define a function to create a new ObservedResource
# Expected responsibility:
# - receive the minimum required technical fields
# - create the database object
# - persist it
# - return the created resource

# TODO: define a function to find an existing ObservedResource
# Expected responsibility:
# - search by stable technical identifier
# - initially this may use normalized_url_hash
# - later this may evolve depending on normalization strategy

# TODO: define a function to update occurrence tracking
# Expected responsibility:
# - increment occurrence_count
# - update last_seen_at
# - persist the changes

# TODO: define a function to get or create an ObservedResource
# Expected responsibility:
# - check whether the resource already exists
# - if it exists, update occurrence tracking
# - if it does not exist, create a new one
# - return the resulting resource

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

# TODO: integrate URL normalization before persistence
# TODO: integrate hashing for normalized URL values
# TODO: connect ObservedResource creation with Analysis creation
# TODO: support repeated occurrence statistics
# TODO: support future domain exposure or leak-related modules carefully