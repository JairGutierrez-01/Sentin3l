from sentin3l.utils import detectors

def test_detect_ip_host():
    # Positive case
    result_ip = detectors.detect_ip_host("192.168.1.50")
    assert result_ip is not None
    assert result_ip["code"] == "IP_IN_HOST"
    assert "192.168.1.50" in result_ip["evidence"]

    # Negative Case
    result_domain = detectors.detect_ip_host("google.com")
    assert result_domain is None

def test_detect_long_url():
    # Positive
    url_muy_larga = "https://example.com/" + ("a" * 100)
    result_long = detectors.detect_long_url(url_muy_larga, limit=100)
    assert result_long is not None
    assert result_long["code"] == "LONG_URL"

    # Negative
    url_corta = "https://example.com/login"
    result_short = detectors.detect_long_url(url_corta, limit=100)
    assert result_short is None

def test_detect_suspicious_tld():
    # Positive
    result_bad_tld = detectors.detect_suspicious_tld("malware-domain.zip")
    assert result_bad_tld is not None
    assert result_bad_tld["code"] == "SUSPICIOUS_TLD"
    assert ".zip" in result_bad_tld["evidence"]

    # Negative
    result_good_tld = detectors.detect_suspicious_tld("forschungsgruppe.de")
    assert result_good_tld is None

def test_detect_sensitive_keywords():
    # Positive
    result_phishing = detectors.detect_sensitive_keywords("https://secure-update.banco.com/verify")
    assert result_phishing is not None
    assert result_phishing["code"] == "SENSITIVE_KEYWORDS"
    assert "verify" in result_phishing["evidence"]
    assert "secure" in result_phishing["evidence"]

    # Negative
    result_clean = detectors.detect_sensitive_keywords("https://mi-blog-personal.com/fotos-viaje")
    assert result_clean is None


def test_detect_punycode():
    result_puny = detectors.detect_punycode("xn--g00gle-hqb.com")
    assert result_puny is not None
    assert result_puny["code"] == "PUNYCODE_DETECTED"

    result_normal = detectors.detect_punycode("google.com")
    assert result_normal is None

def test_detect_excessive_subdomains():
    result_excessive = detectors.detect_excessive_subdomains("login.update.secure.paypal.com")
    assert result_excessive is not None
    assert result_excessive["code"] == "EXCESSIVE_SUBDOMAINS"

    result_normal = detectors.detect_excessive_subdomains("www.paypal.com")
    assert result_normal is None