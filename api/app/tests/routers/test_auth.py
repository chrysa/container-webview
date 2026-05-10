class TestAuthRouter:
    """Unit tests for the /api/auth router."""

    class TestLogin:
        """Tests for POST /api/auth/login."""

        async def test_returns_token_for_valid_credentials(self, api_client, mocker):
            mocker.patch("app.routers.auth._authenticate_ldap", return_value=False)
            mocker.patch("app.routers.auth._authenticate_local", return_value=True)
            async with api_client() as client:
                response = await client.post(
                    "/api/auth/login",
                    data={"username": "admin", "password": "secret"},
                )
            assert response.status_code == 200
            body = response.json()
            assert "access_token" in body
            assert body["token_type"] == "bearer"
            assert body["username"] == "admin"

        async def test_returns_401_for_invalid_credentials(self, api_client, mocker):
            mocker.patch("app.routers.auth._authenticate_ldap", return_value=False)
            mocker.patch("app.routers.auth._authenticate_local", return_value=False)
            async with api_client() as client:
                response = await client.post(
                    "/api/auth/login",
                    data={"username": "admin", "password": "wrong"},
                )
            assert response.status_code == 401

    class TestCheckToken:
        """Tests for GET /api/auth/check."""

        async def test_returns_ok_for_valid_token(self, api_client, auth_headers):
            async with api_client() as client:
                response = await client.get("/api/auth/check", headers=auth_headers())
            assert response.status_code == 200
            assert response.json() == {"status": "ok"}

        async def test_returns_401_without_token(self, api_client):
            async with api_client() as client:
                response = await client.get("/api/auth/check")
            assert response.status_code == 401
