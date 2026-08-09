import hmac
import logging

import bcrypt

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
            import ldap  # noqa: PLC0415 — optional dependency, imported only when LDAP is enabled
        except ImportError:
            _logger.warning("LDAP is configured but python-ldap is not installed; skipping LDAP auth")
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
        """Return True if username/password match the configured admin credentials.

        Verification prefers a bcrypt hash (``admin_password_hash``); a plaintext
        ``admin_password`` is a development-only fallback compared in constant time.
        """
        settings = get_settings()
        if not hmac.compare_digest(username, settings.admin_username):
            return False
        if settings.admin_password_hash:
            try:
                return bcrypt.checkpw(
                    password.encode("utf-8"),
                    settings.admin_password_hash.encode("utf-8"),
                )
            except ValueError:
                _logger.error("admin_password_hash is not a valid bcrypt hash")
                return False
        if settings.admin_password:
            return hmac.compare_digest(password, settings.admin_password)
        return False


auth_service = AuthService()
