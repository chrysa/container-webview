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

