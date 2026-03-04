from datetime import timedelta

import pytest

from app.core.security import create_access_token


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/repairs/",
        "/api/v1/clients/",
        "/api/v1/inventory/",
    ],
)
def test_protected_endpoints_return_current_403_without_token(api_client, path):
    response = api_client.get(path)

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authenticated"


def test_admin_only_endpoint_returns_403_for_customer_role(api_client, customer_token):
    response = api_client.get("/api/v1/users/", headers=_auth_headers(customer_token))

    assert response.status_code == 403
    assert response.json()["detail"] == "Acceso denegado. Solo administradores."


def test_expired_token_returns_401(api_client, admin_account):
    user = admin_account["user"]
    expired_token = create_access_token(
        data={
            "sub": str(user.id),
            "username": user.username,
            "email": user.email,
            "role": user.role,
        },
        expires_delta=timedelta(minutes=-5),
    )

    response = api_client.get("/api/v1/repairs/", headers=_auth_headers(expired_token))

    assert response.status_code == 401
    assert response.json()["detail"] == "Token expirado o inválido"
