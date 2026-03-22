from app.config import get_settings

_LDAP_DN_TEMPLATE: str = "cn={},{}"


class AuthService:
    def authenticate(self, username: str, password: str) -> bool:
        return self._authenticate_ldap(username, password) or self._authenticate_local(username, password)

    def _authenticate_local(self, username: str, password: str) -> bool:
        settings = get_settings()
        return username == settings.admin_username and password == settings.admin_password

    def _authenticate_ldap(self, username: str, password: str) -> bool:
        settings = get_settings()
        if not settings.ldap_server:
            return False
        try:
            import ldap  # type: ignore[import]

            conn = ldap.initialize(settings.ldap_server)
            conn.simple_bind_s(_LDAP_DN_TEMPLATE.format(username, settings.ldap_base_dn), password)
            return True
        except Exception:
            return False


auth_service = AuthService()
