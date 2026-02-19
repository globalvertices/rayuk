"""Tests for authentication endpoints and the health check."""

import pytest
from httpx import AsyncClient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
HEALTH_URL = "/health"

VALID_USER = {
    "email": "alice@example.com",
    "password": "SecurePass123!",
    "first_name": "Alice",
    "last_name": "Smith",
    "role": "tenant",
}


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


class TestHealthCheck:
    async def test_health_returns_200(self, client: AsyncClient):
        response = await client.get(HEALTH_URL)
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


class TestRegister:
    async def test_register_tenant_success(self, client: AsyncClient):
        response = await client.post(REGISTER_URL, json=VALID_USER)
        assert response.status_code == 201

        body = response.json()
        assert body["email"] == VALID_USER["email"]
        assert body["first_name"] == VALID_USER["first_name"]
        assert body["last_name"] == VALID_USER["last_name"]
        assert body["role"] == "tenant"
        assert body["is_email_verified"] is False
        assert "id" in body

    async def test_register_landlord_success(self, client: AsyncClient):
        payload = {**VALID_USER, "email": "bob@example.com", "role": "landlord"}
        response = await client.post(REGISTER_URL, json=payload)
        assert response.status_code == 201
        assert response.json()["role"] == "landlord"

    async def test_register_duplicate_email_returns_409(self, client: AsyncClient):
        # First registration succeeds.
        resp1 = await client.post(REGISTER_URL, json=VALID_USER)
        assert resp1.status_code == 201

        # Second registration with the same email should conflict.
        resp2 = await client.post(REGISTER_URL, json=VALID_USER)
        assert resp2.status_code == 409

    async def test_register_admin_role_rejected(self, client: AsyncClient):
        payload = {**VALID_USER, "role": "admin"}
        response = await client.post(REGISTER_URL, json=payload)
        assert response.status_code == 400

    async def test_register_missing_fields_returns_422(self, client: AsyncClient):
        # Missing required 'email' field.
        payload = {
            "password": "SecurePass123!",
            "first_name": "Alice",
            "last_name": "Smith",
            "role": "tenant",
        }
        response = await client.post(REGISTER_URL, json=payload)
        assert response.status_code == 422

    async def test_register_short_password_returns_422(self, client: AsyncClient):
        payload = {**VALID_USER, "password": "short"}
        response = await client.post(REGISTER_URL, json=payload)
        assert response.status_code == 422

    async def test_register_invalid_email_returns_422(self, client: AsyncClient):
        payload = {**VALID_USER, "email": "not-an-email"}
        response = await client.post(REGISTER_URL, json=payload)
        assert response.status_code == 422

    async def test_register_invalid_role_returns_422(self, client: AsyncClient):
        payload = {**VALID_USER, "role": "superuser"}
        response = await client.post(REGISTER_URL, json=payload)
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------


class TestLogin:
    async def test_login_success(self, client: AsyncClient):
        # Register first.
        reg_resp = await client.post(REGISTER_URL, json=VALID_USER)
        assert reg_resp.status_code == 201

        login_resp = await client.post(
            LOGIN_URL,
            json={"email": VALID_USER["email"], "password": VALID_USER["password"]},
        )
        assert login_resp.status_code == 200

        body = login_resp.json()
        assert "access_token" in body
        assert "refresh_token" in body
        assert body["token_type"] == "bearer"

    async def test_login_wrong_password_returns_401(self, client: AsyncClient):
        await client.post(REGISTER_URL, json=VALID_USER)

        login_resp = await client.post(
            LOGIN_URL,
            json={"email": VALID_USER["email"], "password": "WrongPassword!"},
        )
        assert login_resp.status_code == 401

    async def test_login_nonexistent_user_returns_401(self, client: AsyncClient):
        login_resp = await client.post(
            LOGIN_URL,
            json={"email": "nobody@example.com", "password": "Whatever123!"},
        )
        assert login_resp.status_code == 401

    async def test_login_missing_fields_returns_422(self, client: AsyncClient):
        login_resp = await client.post(LOGIN_URL, json={"email": VALID_USER["email"]})
        assert login_resp.status_code == 422
