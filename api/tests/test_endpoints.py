"""HTTP tests through FastAPI's test client. Needs fastapi and httpx (pip install -r requirements.txt)."""
import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient  # noqa: E402

from api.main import app  # noqa: E402

HORIZON_KEYS = {
    "date",
    "prcp_in",
    "predicted_calls",
    "baseline_calls",
    "extra_calls",
    "spike_probability",
    "risk_level",
    "revenue_if_staffed_usd",
    "overtime_cost_if_unstaffed_usd",
}


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_index(client):
    r = client.get("/")
    assert r.status_code == 200 and r.json()["docs"] == "/docs"


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert set(body) == {
        "status", "model_loaded", "model", "last_data_refresh", "data_file", "data_is_sample", "data_last_date"
    }
    assert body["status"] == "ok"


def test_forecast(client):
    r = client.get("/forecast")
    assert r.status_code == 200
    body = r.json()
    assert set(body) == {"generated_at", "model", "horizon", "assumptions"}
    assert len(body["horizon"]) == 2
    for h in body["horizon"]:
        assert set(h) == HORIZON_KEYS
        assert h["risk_level"] in {"low", "medium", "high"}
    assert set(body["assumptions"]) == {"revenue_per_call_usd", "overtime_cost_per_call_usd"}


def test_what_if(client):
    r = client.post("/forecast/what-if", json={"prcp_in": 4.68, "prior_7d_prcp_in": 0.5, "date": "2023-07-02"})
    assert r.status_code == 200
    body = r.json()
    assert set(body) == HORIZON_KEYS
    assert body["date"] == "2023-07-02" and body["prcp_in"] == 4.68


def test_what_if_only_rain_is_required(client):
    assert client.post("/forecast/what-if", json={"prcp_in": 1.0}).status_code == 200


def test_what_if_rejects_bad_input(client):
    assert client.post("/forecast/what-if", json={"prcp_in": -1}).status_code == 422
    assert client.post("/forecast/what-if", json={}).status_code == 422


def test_history(client):
    rows = client.get("/history").json()
    assert len(rows) == 90
    assert set(rows[0]) == {"date", "actual_calls", "predicted_calls", "prcp_in", "is_spike"}
    assert [r["date"] for r in rows] == sorted(r["date"] for r in rows)
    assert len(client.get("/history?days=7").json()) == 7
    assert client.get("/history?days=0").status_code == 422


def test_dashboard_can_call_it_from_a_browser(client):
    r = client.get("/health", headers={"Origin": "http://localhost:5500"})
    assert r.headers.get("access-control-allow-origin") == "*"
