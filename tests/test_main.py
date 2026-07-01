from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sentin3l.main import app
from sentin3l.database.session import get_db
from sentin3l.services import flag_definition_service

client = TestClient(app)

def test_root():
    """Verifies that the root endpoint successfully serves the frontend HTML template."""
    response = client.get("/")
    assert response.status_code == 200
    # Since it serves HTML via Jinja2, we check the Content-Type header instead of parsing JSON
    assert "text/html" in response.headers["content-type"]


def test_health():
    """Validates the basic health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_api_status():
    """Validates the API system status response."""
    response = client.get("/api/status")
    assert response.status_code == 200
    assert response.json()["api"] == "running"


def test_analyze_safe_url(db_session: Session):
    """Verifies that a known safe URL triggers no threat flags and updates stats."""
    app.dependency_overrides[get_db] = lambda: db_session
    flag_definition_service.seed_default_flags(db_session)

    response = client.post("/api/v1/analyze", json={"url": "https://google.com"})

    assert response.status_code == 200
    data = response.json()
    assert data["target_url"] == "https://google.com/"
    assert data["risk_level"] == "Safe"
    assert data["suspicion_score"] == 0
    assert data["times_analyzed_before"] == 1

    app.dependency_overrides.clear()


def test_analyze_malicious_url(db_session: Session):
    """Verifies that an IP-based URL structure triggers a High-risk verdict with proper evidence."""
    app.dependency_overrides[get_db] = lambda: db_session
    flag_definition_service.seed_default_flags(db_session)

    payload = {"url": "http://192.168.1.100/login/secure"}
    response = client.post("/api/v1/analyze", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["risk_level"] == "High"
    assert data["suspicion_score"] == 90
    assert "IP" in data["explanation_text"]
    assert "login" in data["explanation_text"]

    app.dependency_overrides.clear()


def test_get_recent_activity(db_session: Session):
    """Verifies that the recent feed returns data structures conforming to the AnalysisResponse schema."""
    app.dependency_overrides[get_db] = lambda: db_session
    flag_definition_service.seed_default_flags(db_session)

    payload = {"url": "https://cybersecurity-test.com/login"}
    client.post("/api/v1/analyze", json=payload)

    response = client.get("/api/v1/recent?limit=5")

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 1

    latest = data[0]
    assert "safe_url" in latest
    assert "risk_level" in latest
    assert "suspicion_score" in latest
    assert latest["target_url"] == "cybersecurity-test.com"

    app.dependency_overrides.clear()
