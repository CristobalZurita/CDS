from app.core.business_config import business_config
from app.services.pdf_generator import build_repair_closure_lines


def test_business_config_builds_backend_runtime_strings():
    assert business_config.api_title == "Cirujano de Sintetizadores API"
    assert business_config.quote_delivery_subject("COT-2026-0001") == "Cotización COT-2026-0001 - Cirujano de Sintetizadores"
    assert business_config.appointment_event_title("Cliente Demo") == "Cita: Cliente Demo"
    assert business_config.appointment_event_description("Detalle adicional").startswith(
        "Cita de agendamiento en Cirujano de Sintetizadores"
    )


def test_pdf_generator_uses_canonical_business_labels():
    lines = build_repair_closure_lines(
        {
            "repair_number": "OT-001",
            "client_name": "Cliente Demo",
            "client_email": "cliente@example.com",
            "client_phone": "+56911111111",
            "device_model": "Equipo Demo",
            "device_serial": "SERIAL-001",
            "status_name": "Ingreso",
        }
    )

    assert lines[0] == business_config.repair_closure_pdf_title()
    assert f"{business_config.item_caption()} Equipo Demo" in lines
