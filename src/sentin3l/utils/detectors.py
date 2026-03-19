import logging
import ipaddress
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

def detect_ip_host(hostname: str) -> dict | None:
    try:
        # Intenta parsear como IPv4 o IPv6
        ipaddress.ip_address(hostname)
        return {
            "code": "IP_IN_HOST",
            "evidence": f"The host '{hostname}' is a raw IP address. Legitimate services almost always use domain names.",
        }
    except ValueError:
        return None


def detect_long_url(url: str, limit: int = 100) -> dict | None:
    if len(url) > limit:
        return {
            "code": "LONG_URL",
            "evidence": f"The URL has {len(url)} characters, which is too long and overcomes the recommended limit of {limit}",
        }
    return None


def detect_suspicious_tld(registrable_domain: str, suspicious_tlds: list[str]) -> dict | None:
    try:
        parts = registrable_domain.split('.')
        if len(parts) > 1:
            tld = f".{parts[-1].lower()}"
            if tld in suspicious_tlds:
                return {
                    "code": "SUSPICIOUS_TLD",
                    "evidence": f"High risk TLD using: {tld}"
                }
    except Exception as e:
        logger.error(f"Error detecting with the URL: {e}")
    return None


def detect_sensitive_keywords(url: str, sensitive_keywords: list[str]) -> dict | None:
    url_lower = url.lower()
    found = [word for word in sensitive_keywords if word in url_lower]
    if found:
        return {
            "code": "SENSITIVE_KEYWORDS",
            "evidence": f"Sensitive terms were detected: {', '.join(found)}"
        }
    return None

def detect_punycode(hostname: str) -> dict | None:
    """Detects homograph attacks based on xn-- encoding."""
    if "xn--" in hostname.lower():
        return {
            "code": "PUNYCODE_DETECTED",
            "evidence": "The domain uses Punycode, a common technique for mimicking legitimate sites using special characters."
        }
    return None

def detect_excessive_subdomains(hostname: str) -> dict | None:
    """Count points in the hostname to detect subdomain tunnels."""
    # just real subdomains
    parts = hostname.split('.')
    if len(parts) > 4:  # Example: sub.sub.dominio.com has 4 parts
        return {
            "code": "EXCESSIVE_SUBDOMAINS",
            "evidence": f"{len(parts) - 2} levels of subdomains were detected, which is unusual and is often used to hide the real domain."
        }
    return None

def detect_typosquatting(registrable_domain: str, target_brands: list[str]) -> dict | None:
    """Detects domains that are suspiciously similar to major brands."""
    domain_name = registrable_domain.split('.')[0].lower()

    for brand in target_brands:
        if domain_name == brand: continue

        similarity = SequenceMatcher(None, domain_name, brand).ratio()

        if similarity >= 0.65:
            return {
                "code": "TYPOSQUATTING",
                "evidence": f"The domain '{domain_name}' is suspiciously similar to '{brand}'."
            }
    return None

def detect_url_shortener(hostname: str, url_shorteners: list[str]) -> dict | None:
    """Detects the use of common URL shorteners that hide the final destination."""
    if hostname.lower() in url_shorteners:
        return {
            "code": "URL_SHORTENER",
            "evidence": "This URL uses a shortening service."
        }
    return None

def detect_brand_impersonation(hostname: str, registrable_domain: str, target_brands: list[str]) -> dict | None:
    """Detects brand names in subdomains that don't match the main domain."""
    for brand in target_brands:
        if brand in hostname.lower() and brand not in registrable_domain.lower():
            return {
                "code": "BRAND_IMPERSONATION",
                "evidence": f"The brand '{brand}' appears in the subdomain, but the actual registered domain is '{registrable_domain}'."
            }
    return None

def detect_at_symbol(url: str) -> dict | None:
    if "@" in url:
        return {
            "code": "AT_SYMBOL",
            "evidence": "The use of '@' in a URL is a technique to trick users into seeing a legitimate domain while being redirected elsewhere."
        }
    return None

def detect_double_extension (url_path: str, dangerous_extensions: list[str]) -> dict | None:
    count = sum(1 for ext in dangerous_extensions if ext in url_path.lower())
    if count > 1:
        return {"code": "DOUBLE_EXTENSION", "evidence": "Multiple file extensions detected."}
    return None

def detect_insecure_protocol(url: str) -> dict | None:
    if url.lower().startswith("http://"):
        return {
            "code": "INSECURE_URL",
            "evidence": "The URL uses HTTP instead of HTTPS. Communication is not encrypted, which is dangerous for sensitive actions."
        }
    return None

