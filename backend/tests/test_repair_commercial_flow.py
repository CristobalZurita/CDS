import uuid


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_repair_detail_commercial_flow_connects_warranty_claims_and_payments(
    test_client,
    admin_token,
    customer_account,
):
    slug = uuid.uuid4().hex[:8]

    create_repair_response = test_client.post(
        "/api/v1/repairs/",
        headers=_auth_headers(admin_token),
        json={
            "client_id": customer_account["client"].id,
            "title": f"OT comercial {slug}",
            "description": f"Comercial flow {slug}",
            "labor_cost": 45000,
            "total_cost": 45000,
        },
    )
    assert create_repair_response.status_code in (200, 201), create_repair_response.text
    repair = create_repair_response.json()
    repair_id = repair["id"]

    update_repair_response = test_client.put(
        f"/api/v1/repairs/{repair_id}",
        headers=_auth_headers(admin_token),
        json={
            "work_performed": f"Trabajo comercial {slug}",
            "labor_cost": 45000,
            "total_cost": 45000,
        },
    )
    assert update_repair_response.status_code == 200, update_repair_response.text

    create_warranty_response = test_client.post(
        "/api/v1/warranties/",
        headers=_auth_headers(admin_token),
        json={
            "repair_id": repair_id,
            "warranty_type": "full",
            "duration_days": 90,
            "coverage_description": "Cobertura comercial de prueba",
            "max_claims": 2,
        },
    )
    assert create_warranty_response.status_code == 201, create_warranty_response.text
    warranty = create_warranty_response.json()
    warranty_id = warranty["id"]

    submit_claim_response = test_client.post(
        f"/api/v1/warranties/{warranty_id}/claims",
        headers=_auth_headers(admin_token),
        json={
            "problem_description": "Falla posterior de prueba",
            "fault_type": "audio",
        },
    )
    assert submit_claim_response.status_code == 201, submit_claim_response.text
    claim = submit_claim_response.json()
    assert claim["warranty_id"] == warranty_id

    claims_response = test_client.get(
        f"/api/v1/warranties/{warranty_id}/claims",
        headers=_auth_headers(admin_token),
    )
    assert claims_response.status_code == 200, claims_response.text
    claims = claims_response.json()
    assert len(claims) == 1
    assert claims[0]["claim_number"] == claim["claim_number"]

    create_invoice_response = test_client.post(
        f"/api/v1/invoices/from-repair/{repair_id}",
        headers=_auth_headers(admin_token),
    )
    assert create_invoice_response.status_code == 201, create_invoice_response.text
    invoice = create_invoice_response.json()
    invoice_id = invoice["id"]

    record_payment_response = test_client.post(
        f"/api/v1/invoices/{invoice_id}/payments",
        headers=_auth_headers(admin_token),
        json={
          "amount": 30000,
          "payment_method": "transfer",
          "transaction_id": f"ot-commercial-{slug}",
        },
    )
    assert record_payment_response.status_code == 201, record_payment_response.text
    payment = record_payment_response.json()
    assert payment["invoice_id"] == invoice_id

    payments_response = test_client.get(
        f"/api/v1/payments/?repair_id={repair_id}",
        headers=_auth_headers(admin_token),
    )
    assert payments_response.status_code == 200, payments_response.text
    payments = payments_response.json()
    assert len(payments) == 1
    assert payments[0]["amount"] == 30000
    assert payments[0]["payment_method"] == "transfer"
