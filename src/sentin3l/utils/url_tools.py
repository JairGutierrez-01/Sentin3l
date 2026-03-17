import hashlib
import tldextract
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from typing import Tuple, Dict

def normalize_and_redact_url(raw_url: str) -> str:
    """
    it takes a raw url and normalizes it and redacts it.
    """

    # it disarms the raw URL in a safe way
    parsed = urlparse(raw_url)

    # normalize de domain into non capital letters
    normalized_netloc = parsed.netloc.lower()

    # Redacts the parameters
    query_params = parse_qsl(parsed.query, keep_blank_values=True)

    # Reconstruction of parameters changing the real values into '[REDACTED]'
    redacted_params = [(key, "[REDACTED]") for key, value in query_params]

    # URL encode to join everything
    redacted_query = urlencode(redacted_params)

    # Reconstruction of the whole URL where the fragments are just processed in the users naviugator
    redacted_url = urlunparse((
        parsed.scheme.lower(), #HTTP/HTTPS protocol
        normalized_netloc, #normalized domain
        parsed.path, # path like /login
        parsed.params, # path parameters
        redacted_query, # Censored params
        "" # Fragment eliminated for privacy
    ))
    return redacted_url


def extract_domain_info(raw_url: str) -> Tuple[str, str]:
    """
    Extracts the whole hostname and the registrable domain in a precise way
    """

    # tldextract works even if the URL is "dirty"
    extracted = tldextract.extract(raw_url)
    # union between domain and sufix
    registrable_domain = f"{extracted.domain}.{extracted.suffix}" if extracted.suffix and extracted.domain else ""

    # the whole hostname includes de subdomain if exist
    # fqdn means Fully qualified domain name
    hostname = extracted.fqdn

    return hostname, registrable_domain

def generate_url_hash(redacted_url:str) -> str:
    """
    generates a SHA-256 hash of a redacted URL
    """
    return hashlib.sha256(redacted_url.encode('utf-8')).hexdigest()

def process_url_for_storage(raw_url: str) -> Dict[str, str]:
    """
    Function that will be used for the database
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







