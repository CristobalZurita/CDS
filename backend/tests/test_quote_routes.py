import uuid


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_quote_management_routes_are_available_under_quotation_and_diagnostic(
    test_client,
    admin_token,
):
    email = f"quote-route-{uuid.uuid4().hex[:10]}@example.com"
    create_response = test_client.post(
        "/api/v1/quotations/quotes",
        json={
            "client_name": "Cliente Quotes",
            "client_email": email,
            "problem_description": "Equipo sin audio de salida",
            "estimated_total": 125000,
        },
        headers=_auth_headers(admin_token),
    )
    assert create_response.status_code == 200, create_response.text

    created_quote = create_response.json()
    quote_id = created_quote["id"]
    quote_number = created_quote["quote_number"]

    canonical_board = test_client.get(
        "/api/v1/quotations/quotes/board",
        headers=_auth_headers(admin_token),
    )
    legacy_board = test_client.get(
        "/api/v1/diagnostic/quotes/board",
        headers=_auth_headers(admin_token),
    )
    assert canonical_board.status_code == 200, canonical_board.text
    assert legacy_board.status_code == 200, legacy_board.text
    assert canonical_board.json() == legacy_board.json()

    canonical_detail = test_client.get(
        f"/api/v1/quotations/quotes/{quote_id}",
        headers=_auth_headers(admin_token),
    )
    legacy_detail = test_client.get(
        f"/api/v1/diagnostic/quotes/{quote_id}",
        headers=_auth_headers(admin_token),
    )
    assert canonical_detail.status_code == 200, canonical_detail.text
    assert legacy_detail.status_code == 200, legacy_detail.text
    assert canonical_detail.json() == legacy_detail.json()
    assert canonical_detail.json()["quote_number"] == quote_number


def test_openapi_marks_quotation_as_canonical_and_diagnostic_as_compatibility(test_client):
    paths = test_client.app.openapi()["paths"]

    assert paths["/api/v1/quotations/estimate"]["post"].get("deprecated") is not True
    assert paths["/api/v1/diagnostic/calculate"]["post"]["deprecated"] is True
    assert paths["/api/v1/diagnostic/quotes"]["get"]["deprecated"] is True
    assert paths["/api/v1/diagnostic/quotes"]["post"]["deprecated"] is True
    assert paths["/api/v1/diagnostic/quotes/board"]["get"]["deprecated"] is True
    assert paths["/api/v1/ai/analyze"]["post"]["deprecated"] is True


def test_quote_send_route_keeps_delivery_contract(
    test_client,
    admin_token,
    monkeypatch,
):
    sent_payloads = []

    def _fake_send_email(self, *, to_email, subject, html_content):
        sent_payloads.append(
            {
                "to_email": to_email,
                "subject": subject,
                "html_content": html_content,
            }
        )
        return True

    monkeypatch.setattr(
        "app.services.email_service.EmailService.send_email",
        _fake_send_email,
    )

    email = f"quote-send-{uuid.uuid4().hex[:10]}@example.com"
    create_response = test_client.post(
        "/api/v1/quotations/quotes",
        json={
            "client_name": "Cliente Send",
            "client_email": email,
            "problem_description": "Equipo enciende pero no responde el panel",
            "estimated_total": 189000,
        },
        headers=_auth_headers(admin_token),
    )
    assert create_response.status_code == 200, create_response.text

    created_quote = create_response.json()
    send_response = test_client.post(
        f"/api/v1/quotations/quotes/{created_quote['id']}/send",
        json={"message": "Revision tecnica incluida", "send_whatsapp": False},
        headers=_auth_headers(admin_token),
    )
    assert send_response.status_code == 200, send_response.text

    sent_quote = send_response.json()
    assert sent_quote["sent_to"] == [email]
    assert sent_quote["failed_to"] == []
    assert sent_quote["whatsapp_queued"] is False
    assert sent_quote["quote"]["status"] == "sent"
    assert sent_payloads and sent_payloads[0]["to_email"] == email
    assert created_quote["quote_number"] in sent_payloads[0]["subject"]
