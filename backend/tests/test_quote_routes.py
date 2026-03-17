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
