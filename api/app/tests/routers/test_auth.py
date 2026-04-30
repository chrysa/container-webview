<<<<<<< HEAD
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
||||||| parent of 62afd77 (test(api): add unit tests, fix guidelines violations, update docs\n\n- Single outer test class with nested sub-classes (no multiple module-level classes)\n- No type annotations in test helpers or factory functions\n- No imports inside fixture/method bodies\n- No noqa comments\n- mocker.patch for all mocking, Given-When-Then docstrings\n- conftest: move security import to module level\n- docs: rewrite README, update changelog, fix stale make targets")
=======
class TestAuthRouter:
    """Unit tests for the /api/auth router."""

    class TestLogin:
        """Tests for POST /api/auth/login."""

        async def test_returns_token_for_valid_credentials(self, api_client, mocker):
            """Return 200 with a JWT token when credentials are correct.

            Given: auth_service.authenticate returns True
            When: POST /api/auth/login with any credentials
            Then: Should return 200 with access_token, token_type and username
            """
            mocker.patch(
                "app.routers.auth.auth_service.authenticate",
                return_value=True,
            )
            async with api_client() as client:
                response = await client.post(
                    "/api/auth/login",
                    data={"username": "admin", "password": "secret"},
                )

            assert response.status_code == 200, f"Expected 200 but got {response.status_code=}"
            body = response.json()
            assert "access_token" in body, f"Expected access_token in {body=}"
            assert body["token_type"] == "bearer", f"Expected 'bearer' but got {body['token_type']=}"
            assert body["username"] == "admin", f"Expected 'admin' but got {body['username']=}"

        async def test_returns_401_for_invalid_credentials(self, api_client, mocker):
            """Return 401 when credentials are wrong.

            Given: auth_service.authenticate returns False
            When: POST /api/auth/login with wrong password
            Then: Should return 401
            """
            mocker.patch(
                "app.routers.auth.auth_service.authenticate",
                return_value=False,
            )
            async with api_client() as client:
                response = await client.post(
                    "/api/auth/login",
                    data={"username": "admin", "password": "wrong"},
                )

            assert response.status_code == 401, f"Expected 401 but got {response.status_code=}"

    class TestCheckToken:
        """Tests for GET /api/auth/check."""

        async def test_returns_ok_for_valid_token(self, api_client, auth_headers):
            """Return 200 with status ok when the token is valid.

            Given: A valid Bearer JWT token
            When: GET /api/auth/check with Authorization header
            Then: Should return 200 {"status": "ok"}
            """
            async with api_client() as client:
                response = await client.get("/api/auth/check", headers=auth_headers())

            assert response.status_code == 200, f"Expected 200 but got {response.status_code=}"
            assert response.json() == {"status": "ok"}, f"Unexpected body {response.json()=}"

        async def test_returns_401_without_token(self, api_client):
            """Return 401 when no Authorization header is provided.

            Given: No Authorization header
            When: GET /api/auth/check
            Then: Should return 401
            """
            async with api_client() as client:
                response = await client.get("/api/auth/check")

            assert response.status_code == 401, f"Expected 401 but got {response.status_code=}"

>>>>>>> 62afd77 (test(api): add unit tests, fix guidelines violations, update docs\n\n- Single outer test class with nested sub-classes (no multiple module-level classes)\n- No type annotations in test helpers or factory functions\n- No imports inside fixture/method bodies\n- No noqa comments\n- mocker.patch for all mocking, Given-When-Then docstrings\n- conftest: move security import to module level\n- docs: rewrite README, update changelog, fix stale make targets")
