import os
from pathlib import Path

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[2]
DB_PATH = Path(os.getenv("TEST_DB_PATH", str(ROOT / "backend" / "tests" / "test_cirujano.db")))

os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = f"sqlite:///{DB_PATH}"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["JWT_REFRESH_SECRET"] = "test-refresh-secret"
os.environ["SKIP_MIGRATIONS"] = "1"
os.environ["TURNSTILE_DISABLE"] = "true"

from app.main import app
from app.routers.quotation import INSTRUMENTS


INSTRUMENT_ID = next(
    instrument_id
    for instrument_id, instrument in INSTRUMENTS.items()
    if "rack" not in str(instrument.get("model") or "").lower()
)


def test_guided_estimate_blocks_downstream_branches_when_instrument_has_no_power():
    with TestClient(app) as client:
        low_response = client.post(
            "/api/v1/quotations/estimate",
            json={
                "instrument_id": INSTRUMENT_ID,
                "guided_answers": {
                    "power": "powers_on",
                    "audio": "none",
                    "keyboard": "single_key",
                    "controls": "none",
                    "display": "none",
                    "connectivity": "none",
                    "cosmetic": "none",
                },
                "selected_symptoms": ["single_key"],
                "customer_notes": "",
                "visual_issue_count": 0,
                "marked_faults": [],
                "turnstile_token": "test-bypass",
            },
        )
        assert low_response.status_code == 200, low_response.text

        high_response = client.post(
            "/api/v1/quotations/estimate",
            json={
                "instrument_id": INSTRUMENT_ID,
                "guided_answers": {
                    "power": "no_power",
                    "audio": "one_side",
                    "keyboard": "multiple_keys",
                    "controls": "multiple_controls",
                    "display": "broken_display",
                    "connectivity": "usb_fault",
                    "cosmetic": "heavy_damage",
                },
                "selected_symptoms": ["no_power", "one_side", "multiple_keys"],
                "customer_notes": "Antes fallaba una tecla y el audio salia por un lado.",
                "visual_issue_count": 2,
                "marked_faults": ["fuente", "audio"],
                "turnstile_token": "test-bypass",
            },
        )
        assert high_response.status_code == 200, high_response.text

    low_body = low_response.json()
    high_body = high_response.json()

    assert low_body["summary"]["mode"] == "guided"
    assert low_body["summary"]["blocked_by_power"] is False
    assert high_body["summary"]["mode"] == "guided"
    assert high_body["summary"]["blocked_by_power"] is True
    assert high_body["summary"]["notes_present"] is True
    assert high_body["summary"]["main_issue"] == "no_power"
    assert high_body["summary"]["range_label"] == "Estimación referencial"
    assert high_body["min_price"] >= 40000
    assert high_body["max_price"] <= 150000
    assert high_body["min_price"] <= high_body["max_price"]
    assert high_body["min_price"] >= low_body["min_price"]
    assert high_body["max_price"] >= low_body["max_price"]
    assert high_body["breakdown"] == []


def test_legacy_fault_estimate_keeps_power_precedence_and_fault_mode_summary():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/quotations/estimate",
            json={
                "instrument_id": INSTRUMENT_ID,
                "faults": ["POWER", "AUDIO_NO_OUTPUT", "BUTTON_DEAD"],
                "turnstile_token": "test-bypass",
            },
        )

    assert response.status_code == 200, response.text

    body = response.json()
    assert body["summary"]["mode"] == "faults"
    assert body["summary"]["blocked_by_power"] is True
    assert body["summary"]["selected_symptom_count"] == 3
    assert len(body["breakdown"]) == 1
    assert body["breakdown"][0]["fault_id"] == "POWER"
    assert body["min_price"] <= body["max_price"]
