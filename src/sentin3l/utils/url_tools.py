import hashlib
import tldextract
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from typing import Tuple, Dict

def normalize_and_redact_url(raw_url: str) -> str:
    """
    Normalizes a raw URL and redacts its query parameters for user privacy.

    Converts the scheme and netloc to lowercase, replaces all query parameter
    values with '[REDACTED]', and drops the URL fragment (hash) since it is
    only processed client-side by the browser.

    Args:
        raw_url (str): The original, raw URL string submitted by the user.

    Returns:
        str: The sanitized and normalized URL string, safe for logging or analysis.
    """
    # Safely disarm the raw URL
    parsed = urlparse(raw_url)

    # Normalize the domain to lowercase
    normalized_netloc = parsed.netloc.lower()

    # Extract query parameters
    query_params = parse_qsl(parsed.query, keep_blank_values=True)

    # Reconstruct parameters by changing real values to '[REDACTED]'
    redacted_params = [(key, "[REDACTED]") for key, value in query_params]

    # URL encode to assemble them back
    redacted_query = urlencode(redacted_params)

    # Reconstruct the full sanitized URL
    redacted_url = urlunparse((
        parsed.scheme.lower(),  # HTTP/HTTPS protocol normalization
        normalized_netloc,      # Normalized domain/host
        parsed.path,            # Path (e.g., /login)
        parsed.params,          # Path parameters
        redacted_query,         # Censored query parameters
        ""                      # Fragment eliminated for privacy principles
    ))
    return redacted_url


def extract_domain_info(raw_url: str) -> Tuple[str, str]:
    """
    Extracts the full hostname and the registrable domain from a URL.

    Leverages `tldextract` to accurately handle complex public suffixes
    (e.g., .co.uk) and IP addresses, preventing common parsing bypasses.

    Args:
        raw_url (str): The target URL to extract domain data from.

    Returns:
        Tuple[str, str]: A tuple containing:
            - hostname (str): The full host (e.g., 'sub.domain.com' or '192.168.1.1').
            - registrable_domain (str): The base paid domain (e.g., 'domain.com').
    """
    parsed = urlparse(raw_url)
    hostname = parsed.hostname or ""

    extracted = tldextract.extract(raw_url)

    if extracted.suffix and extracted.domain:
        registrable_domain = f"{extracted.domain}.{extracted.suffix}"
    else:
        registrable_domain = extracted.domain

    return hostname, registrable_domain


def generate_url_hash(redacted_url: str) -> str:
    """
    Generates a SHA-256 cryptographic hash of a redacted URL.

    This hash serves as a unique identifier for tracking repeated observations
    without persisting sensitive input history in the database.

    Args:
        redacted_url (str): The pre-processed and anonymized safe URL.

    Returns:
        str: A 64-character hexadecimal string representing the SHA-256 hash.
    """
    return hashlib.sha256(redacted_url.encode('utf-8')).hexdigest()


def process_url_for_storage(raw_url: str) -> Dict[str, str]:
    """
    Orchestrates the preparation and metadata extraction of an incoming URL.

    This is the primary utility function invoked before persisting a resource
    into the 'ObservedResource' database model. It executes normalization,
    privacy-focused hashing, and domain extraction.

    Args:
        raw_url (str): The raw URL string received by the system pipeline.

    Returns:
        Dict[str, str]: A dictionary structured for database mapping containing:
            - safe_url: Parameter-redacted URL string.
            - normalized_url_hash: Unique SHA-256 hash of the safe URL.
            - hostname: Extracted network location host.
            - registrable_domain: Extracted root domain.
    """
    safe_url = normalize_and_redact_url(raw_url)
    url_hash = generate_url_hash(safe_url)
    hostname, registrable_domain = extract_domain_info(raw_url)

    return {
        "safe_url": safe_url,
        "normalized_url_hash": url_hash,
        "hostname": hostname,
        "registrable_domain": registrable_domain
    }





