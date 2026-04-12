from faker import Faker
from httpx import ASGITransport
from httpx import AsyncClient
import pytest

from app.config import Settings
from app.config import get_settings
from app.main import app


@pytest.fixture(name="faker_instance")
def fixt_faker_instance():
    def _load(**kwargs):
        locale = kwargs.get("locale", "en_US")
        return Faker(locale)

    return _load


@pytest.fixture(name="fake")
def fixt_fake():
    return Faker("en_US")


@pytest.fixture(name="test_settings")
def fixt_test_settings(tmp_path):
    """Override settings to use a temp projects directory and known credentials."""

    def _load(**kwargs):
        return Settings(
            secret_key=kwargs.get("secret_key", "test-secret-key-for-tests"),
            admin_username=kwargs.get("admin_username", "testuser"),
            admin_password=kwargs.get("admin_password", "testpass"),
            projects_path=kwargs.get("projects_path", str(tmp_path)),
            ldap_server="",
        )

    return _load


@pytest.fixture(name="override_settings")
def fixt_override_settings(test_settings):
    """Patch get_settings() for the duration of a test."""

    def _load(**kwargs):
        settings = test_settings(**kwargs)
        app.dependency_overrides[get_settings] = lambda: settings
        get_settings.cache_clear()
        return settings

    yield _load
    app.dependency_overrides.pop(get_settings, None)
    get_settings.cache_clear()


@pytest.fixture(name="api_client")
async def fixt_api_client(override_settings):
    """Authenticated async HTTP client against the FastAPI app."""

    def _load(**kwargs):
        override_settings(**kwargs)
        return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")

    return _load


@pytest.fixture(name="valid_token")
def fixt_valid_token():
    """Return a valid JWT token for test authentication."""
    from app.security import security  # noqa: PLC0415

    def _load(**kwargs):
        get_settings.cache_clear()
        return security.create_access_token(kwargs.get("username", "testuser"))

    return _load


@pytest.fixture(name="auth_headers")
def fixt_auth_headers(valid_token):
    """Return Authorization headers for a test JWT token."""

    def _load(**kwargs):
        token = valid_token(**kwargs)
        return {"Authorization": f"Bearer {token}"}

    return _load
