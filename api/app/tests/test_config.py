import secrets

import pytest

from app.config import INSECURE_SECRET_KEY
from app.config import InsecureConfigurationError
from app.config import Settings


def _settings(**kwargs) -> Settings:
    """Build Settings with explicit values so the host environment cannot leak in."""
    defaults = {
        "secret_key": INSECURE_SECRET_KEY,
        "ldap_server": "",
        "admin_password": "",
        "admin_password_hash": "",
    }
    defaults.update(kwargs)
    return Settings(_env_file=None, **defaults)


class TestSettingsGuard:
    """Unit tests for the Settings secure-config guard."""

    @pytest.mark.parametrize("environment", ["production", "staging", "prod", "PRODUCTION"])
    def test_rejects_sentinel_secret_outside_dev_and_test(self, environment):
        """Refuse the example SECRET_KEY outside explicit development/test environments.

        Given: The sentinel secret_key and a non development/test environment
        When: Building Settings
        Then: Should raise InsecureConfigurationError mentioning secret_key
        """
        with pytest.raises(InsecureConfigurationError, match="secret_key"):
            _settings(environment=environment, ldap_server="ldap://ldap.example.com")

    @pytest.mark.parametrize("environment", ["staging", "production"])
    def test_rejects_empty_secret_outside_dev_and_test(self, environment):
        """Refuse an empty SECRET_KEY outside explicit development/test environments.

        Given: An empty secret_key and a non development/test environment
        When: Building Settings
        Then: Should raise InsecureConfigurationError
        """
        with pytest.raises(InsecureConfigurationError, match="secret_key"):
            _settings(environment=environment, secret_key="", ldap_server="ldap://ldap.example.com")

    @pytest.mark.parametrize("environment", ["development", "test", "Development"])
    def test_tolerates_sentinel_secret_in_dev_and_test(self, environment):
        """Accept the example SECRET_KEY in explicit development/test environments.

        Given: The sentinel secret_key and a development/test environment
        When: Building Settings
        Then: Should not raise
        """
        settings = _settings(environment=environment)
        assert settings.secret_key == INSECURE_SECRET_KEY, f"Unexpected {settings.secret_key=}"

    def test_accepts_strong_secret_in_production(self):
        """Accept a non-default SECRET_KEY in production when an auth backend is set.

        Given: A random secret_key, production environment and an LDAP server
        When: Building Settings
        Then: Should not raise
        """
        strong = secrets.token_urlsafe(32)
        settings = _settings(environment="production", secret_key=strong, ldap_server="ldap://ldap.example.com")
        assert settings.secret_key == strong, "Expected the provided secret_key to be kept"

    def test_rejects_plaintext_admin_in_production(self):
        """Keep refusing a plaintext-only local admin in production.

        Given: A strong secret_key, production, no LDAP and no admin_password_hash
        When: Building Settings
        Then: Should raise InsecureConfigurationError mentioning admin_password_hash
        """
        with pytest.raises(InsecureConfigurationError, match="admin_password_hash"):
            _settings(environment="production", secret_key=secrets.token_urlsafe(32))

    def test_staging_does_not_require_admin_hash(self):
        """Only production enforces the bcrypt admin hash requirement.

        Given: A strong secret_key, staging, no LDAP and no admin_password_hash
        When: Building Settings
        Then: Should not raise
        """
        settings = _settings(environment="staging", secret_key=secrets.token_urlsafe(32))
        assert settings.environment == "staging", f"Unexpected {settings.environment=}"
