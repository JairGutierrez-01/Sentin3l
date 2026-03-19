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
    mock_tlds = [".zip", ".tk", ".top"]

    # Positive
    result_bad_tld = detectors.detect_suspicious_tld("malware-domain.zip", mock_tlds)
    assert result_bad_tld is not None
    assert result_bad_tld["code"] == "SUSPICIOUS_TLD"
    assert ".zip" in result_bad_tld["evidence"]

    # Negative
    result_good_tld = detectors.detect_suspicious_tld("forschungsgruppe.de", mock_tlds)
    assert result_good_tld is None


def test_detect_sensitive_keywords():
    mock_keywords = ["login", "verify", "secure"]

    # Positive
    result_phishing = detectors.detect_sensitive_keywords("https://secure-update.banco.com/verify", mock_keywords)
    assert result_phishing is not None
    assert result_phishing["code"] == "SENSITIVE_KEYWORDS"
    assert "verify" in result_phishing["evidence"]
    assert "secure" in result_phishing["evidence"]

    # Negative
    result_clean = detectors.detect_sensitive_keywords("https://mi-blog-personal.com/fotos-viaje", mock_keywords)
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


def test_detect_typosquatting():
    marcas = ["google", "paypal", "microsoft"]

    # Positive
    result_typo = detectors.detect_typosquatting("g00gle.com", marcas)
    assert result_typo is not None
    assert result_typo["code"] == "TYPOSQUATTING"
    assert "g00gle" in result_typo["evidence"]

    # Negative
    result_safe = detectors.detect_typosquatting("google.com", marcas)
    assert result_safe is None


def test_detect_url_shortener():
    mock_shorteners = ["bit.ly", "t.co", "tinyurl.com"]

    # Positive
    result_short = detectors.detect_url_shortener("bit.ly", mock_shorteners)
    assert result_short is not None
    assert result_short["code"] == "URL_SHORTENER"

    # Negative
    result_long = detectors.detect_url_shortener("my-university.de", mock_shorteners)
    assert result_long is None


def test_detect_brand_impersonation():
    marcas = ["paypal", "apple"]

    # Positive
    result_impersonate = detectors.detect_brand_impersonation("paypal.verification-security.com",
                                                              "verification.security.com", marcas)
    assert result_impersonate is not None
    assert result_impersonate["code"] == "BRAND_IMPERSONATION"

    # Negative
    result_safe = detectors.detect_brand_impersonation("www.paypal.com", "paypal.com", marcas)
    assert result_safe is None


def test_detect_at_symbol():
    # Positive
    result_at = detectors.detect_at_symbol("https://google.com@evilsite.ru/login")
    assert result_at is not None
    assert result_at["code"] == "AT_SYMBOL"

    # Negative
    result_clean = detectors.detect_at_symbol("https://google.com/login")
    assert result_clean is None


def test_detect_double_extension():
    mock_exts = [".html", ".php", ".exe", ".zip", ".pdf"]

    # Positive
    result_double = detectors.detect_double_extension("/downloads/ticket.pdf.exe", mock_exts)
    assert result_double is not None
    assert result_double["code"] == "DOUBLE_EXTENSION"

    # Negative
    result_single = detectors.detect_double_extension("/downloads/ticket.pdf", mock_exts)
    assert result_single is None


def test_detect_insecure_protocol():
    # Positive
    result_http = detectors.detect_insecure_protocol("http://local-bank.de/login")
    assert result_http is not None
    assert result_http["code"] == "INSECURE_URL"

    result_https = detectors.detect_insecure_protocol("https://local-bank.de/login")
    assert result_https is None