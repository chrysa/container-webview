import pytest


class TestLoginEndpoint:
    """Tests for POST /api/auth/login."""

    async def test_login_success_returns_token(self, override_settings, api_client):
        """Return a JWT token on successful local authentication.

        Given: Valid admin credentials configured via settings
        When: POST /api/auth/login with correct username and password
        Then: Should return 200 with access_token, token_type=bearer and username
        """
        override_settings(admin_username="admin", admin_password="secret")
        async with api_client(admin_username="admin", admin_password="secret") as client:
            response = await client.post(
                "/api/auth/login",
                data={"username": "admin", "password": "secret"},
            )

        assert response.status_code == 200, f"Expected 200 but got {response.status_code=}"
        body = response.json()
        assert "access_token" in body, f"Missing access_token in {body=}"
        assert body["token_type"] == "bearer", f"Unexpected {body['token_type']=}"
        assert body["username"] == "admin", f"Unexpected {body['username']=}"

    async def test_login_wrong_password_returns_401(self, override_settings, api_client):
        """Reject login with wrong password.

        Given: Admin credentials with known password
        When: POST /api/auth/login with wrong password
        Then: Should return 401 Unauthorized
        """
        override_settings(admin_username="admin", admin_password="correct")
        async with api_client(admin_username="admin", admin_password="correct") as client:
            response = await client.post(
                "/api/auth/login",
                data={"username": "admin", "password": "wrong"},
            )

        assert response.status_code == 401, f"Expected 401 but got {response.status_code=}"

    async def test_login_unknown_user_returns_401(self, override_settings, api_client):
        """Reject login with unknown username.

        Given: Admin configured with a specific username
        When: POST /api/auth/login with different username
        Then: Should return 401 Unauthorized
        """
        override_settings(admin_username="admin", admin_password="secret")
        async with api_client(admin_username="admin", admin_password="secret") as client:
            response = await client.post(
                "/api/auth/login",
                data={"username": "nobody", "password": "secret"},
            )

        assert response.status_code == 401, f"Expected 401 but got {response.status_code=}"

    @pytest.mark.parametrize(
        "payload",
        [
            {},
            {"username": "admin"},
            {"password": "secret"},
        ],
    )
    async def test_login_missing_fields_returns_422(self, api_client, payload):
        """Reject login with missing form fields.

        Given: An incomplete form payload
        When: POST /api/auth/login with missing required fields
        Then: Should return 422 Unprocessable Entity
        """
        async with api_client() as client:
            response = await client.post("/api/auth/login", data=payload)

        assert response.status_code == 422, f"Expected 422 but got {response.status_code=} for {payload=}"


class TestCheckEndpoint:
    """Tests for GET /api/auth/check."""

    async def test_check_with_valid_token_returns_ok(self, api_client, auth_headers):
        """Return ok when bearer token is valid.

        Given: A valid JWT access token in the Authorization header
        When: GET /api/auth/check
        Then: Should return 200 with {"status": "ok"}
        """
        async with api_client() as client:
            response = await client.get("/api/auth/check", headers=auth_headers())

        assert response.status_code == 200, f"Expected 200 but got {response.status_code=}"
        assert response.json() == {"status": "ok"}, f"Unexpected body: {response.json()=}"

    async def test_check_without_token_returns_401(self, api_client):
        """Reject request without Authorization header.

        Given: No authentication header
        When: GET /api/auth/check
        Then: Should return 401 Unauthorized
        """
        async with api_client() as client:
            response = await client.get("/api/auth/check")

        assert response.status_code == 401, f"Expected 401 but got {response.status_code=}"

    async def test_check_with_invalid_token_returns_401(self, api_client):
        """Reject request with a malformed or expired token.

        Given: An invalid bearer token
        When: GET /api/auth/check with bad token
        Then: Should return 401 Unauthorized
        """
        async with api_client() as client:
            response = await client.get(
                "/api/auth/check",
                headers={"Authorization": "Bearer invalid.token.here"},
            )

        assert response.status_code == 401, f"Expected 401 but got {response.status_code=}"
