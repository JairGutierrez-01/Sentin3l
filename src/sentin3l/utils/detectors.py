import re
import logging

logger = logging.getLogger(__name__)

def detect_ip_host(hostname: str) -> dict | None:

    # Simple regex to detect patterns in IPv4
    ip_pattern = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"

    if re.match(ip_pattern, hostname):
        return {
            "code": "IP_IN_HOST",
            "evidence": f"The Host '{hostname}' is an IP address, which is really inusual for legit sites",
        }
    return None


def detect_long_url(safe_url: str, limit: int = 100) -> dict | None:
    if len(safe_url) > limit:
        return {
            "code": "LONG_URL",
            "evidence": f"The URL has {len(safe_url)} characters, which is too long and overcomes the recommended limit of {limit}",
        }
    return None


def detect_suspicious_tld(registrable_domain: str) -> dict | None:

    high_risk_tlds = {".zip", ".top", ".xyz", ".pw", ".tk"}

    try:
        parts = registrable_domain.split('.')
        if len(parts) > 1:
            tld = f".{parts[-1].lower()}"
            if tld in high_risk_tlds:
                return {
                    "code": "SUSPICIOUS_TLD",
                    "evidence": f"TLD de alto riesgo usado: {tld}"
                }
    except Exception as e:
        logger.error(f"Error detecting with the URL: {e}")
    return None


def detect_sensitive_keywords(safe_url: str) -> dict | None:

    keywords = ["login", "verify", "secure", "update", "banking", "confirm"]
    url_lower = safe_url.lower()

    found = [word for word in keywords if word in url_lower]

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