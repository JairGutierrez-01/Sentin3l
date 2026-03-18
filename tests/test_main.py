from sentin3l.database.session import get_db
from sentin3l.services import flag_definition_service
from fastapi.testclient import TestClient
from sentin3l.main import app
from sentin3l.database.session import get_db
from sentin3l.services import flag_definition_service

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["system"] == "Sentin3l"


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_analyze_safe_url(db_session):
    app.dependency_overrides[get_db] = lambda: db_session

    flag_definition_service.seed_default_flags(db_session)

    response = client.post("/api/v1/analyze", json={"url": "https://google.com"})

    assert response.status_code == 200
    data = response.json()
    assert data["target_url"] == "https://google.com"
    assert data["verdict"] == "Safe"
    assert data["suspicion_score"] == 0
    assert data["times_analyzed_before"] == 1

    app.dependency_overrides.clear()


def test_analyze_malicious_url(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    flag_definition_service.seed_default_flags(db_session)

    payload = {"url": "http://192.168.1.100/login/secure"}
    response = client.post("/api/v1/analyze", json=payload)

    assert response.status_code == 200
    data = response.json()

    print(f"\n--- REPORTE DE LA API: {data} ---\n")

    assert data["verdict"] == "High"
    assert data["suspicion_score"] == 75
    assert "IP" in data["explanation"]
    assert "login" in data["explanation"]

    app.dependency_overrides.clear()
