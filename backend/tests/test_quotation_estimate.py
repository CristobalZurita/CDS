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
from app.services.reference_catalog_service import get_reference_catalog

CATALOG = get_reference_catalog()

# Guard: si no hay instrumentos sin "rack" en el modelo, saltear todo el módulo.
_candidates = [
    instrument["id"]
    for instrument in CATALOG["instruments"]
    if "rack" not in str(instrument.get("model") or "").lower()
]
if not _candidates:
    import pytest
    pytest.skip(
        "No hay instrumentos no-rack en INSTRUMENTS — instrumentos.json vacío o no disponible.",
        allow_module_level=True,
    )

INSTRUMENT_ID = _candidates[0]
INSTRUMENT = CATALOG["instruments_by_id"][INSTRUMENT_ID]
BRAND_ID = INSTRUMENT["brand"]


def test_quotation_catalog_endpoints_match_diagnostic_catalog():
    with TestClient(app) as client:
        quotation_brands = client.get("/api/v1/quotations/instruments/brands")
        diagnostic_brands = client.get("/api/v1/diagnostic/instruments/brands")
        assert quotation_brands.status_code == 200, quotation_brands.text
        assert diagnostic_brands.status_code == 200, diagnostic_brands.text

        quotation_models = client.get(f"/api/v1/quotations/instruments/models/{BRAND_ID}")
        diagnostic_models = client.get(f"/api/v1/diagnostic/instruments/models/{BRAND_ID}")
        assert quotation_models.status_code == 200, quotation_models.text
        assert diagnostic_models.status_code == 200, diagnostic_models.text

        quotation_faults = client.get(f"/api/v1/quotations/faults/applicable/{INSTRUMENT_ID}")
        diagnostic_faults = client.get(f"/api/v1/diagnostic/faults/applicable/{INSTRUMENT_ID}")
        assert quotation_faults.status_code == 200, quotation_faults.text
        assert diagnostic_faults.status_code == 200, diagnostic_faults.text

    assert quotation_brands.json() == diagnostic_brands.json()
    assert quotation_models.json() == diagnostic_models.json()
    assert quotation_faults.json() == diagnostic_faults.json()


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


def test_fault_estimate_aligns_with_diagnostic_calculate():
    with TestClient(app) as client:
        quotation_response = client.post(
            "/api/v1/quotations/estimate",
            json={
                "instrument_id": INSTRUMENT_ID,
                "faults": ["AUDIO_NO_OUTPUT", "BUTTON_DEAD"],
                "turnstile_token": "test-bypass",
            },
        )
        assert quotation_response.status_code == 200, quotation_response.text

        instrument = CATALOG["instruments_by_id"][INSTRUMENT_ID]
        diagnostic_response = client.post(
            "/api/v1/diagnostic/calculate",
            json={
                "equipment": {
                    "brand": instrument["brand"],
                    "model": instrument["id"],
                },
                "faults": ["AUDIO_NO_OUTPUT", "BUTTON_DEAD"],
            },
        )
        assert diagnostic_response.status_code == 200, diagnostic_response.text

    quotation_body = quotation_response.json()
    diagnostic_body = diagnostic_response.json()

    assert quotation_body["base_total"] == diagnostic_body["base_cost"]
    assert quotation_body["summary"]["complexity_factor"] == diagnostic_body["complexity_factor"]
    assert quotation_body["summary"]["value_factor"] == diagnostic_body["value_factor"]
    assert quotation_body["summary"]["final_cost"] == diagnostic_body["final_cost"]
