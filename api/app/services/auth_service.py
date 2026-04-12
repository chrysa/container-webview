import logging

import ldap  # type: ignore[import]

from app.config import get_settings


_logger = logging.getLogger(__name__)
_LDAP_DN_TEMPLATE: str = "cn={},{}"


class AuthService:
    """Authenticates users via local credentials or an LDAP server."""

    def authenticate(self, username: str, password: str) -> bool:
        """Return True if the user can be authenticated by any configured method."""
        return self._authenticate_ldap(username, password) or self._authenticate_local(username, password)

    def _authenticate_ldap(self, username: str, password: str) -> bool:
        """Return True if the user can bind to the configured LDAP server."""
        settings = get_settings()
        if not settings.ldap_server:
            return False
        try:
            conn = ldap.initialize(settings.ldap_server)
            conn.simple_bind_s(
                _LDAP_DN_TEMPLATE.format(username, settings.ldap_base_dn),
                password,
            )
        except ldap.LDAPError as ldap_exc:
            _logger.debug("LDAP authentication failed for user %r: %s", username, ldap_exc)
            return False
        return True

    def _authenticate_local(self, username: str, password: str) -> bool:
        """Return True if username/password match the configured admin credentials."""
        settings = get_settings()
        return username == settings.admin_username and password == settings.admin_password


auth_service = AuthService()
