import ldap
import pytest

from app.services.auth_service import AuthService


class TestAuthService:
    """Unit tests for AuthService."""

    class TestAuthenticateLocal:
        """Tests for _authenticate_local()."""

        def test_returns_true_for_valid_credentials(self, mocker):
            """Return True when username and password match admin settings.

            Given: Settings with admin_username='admin' and admin_password='secret'
            When: Calling _authenticate_local('admin', 'secret')
            Then: Should return True
            """
            mocker.patch(
                "app.services.auth_service.get_settings",
                return_value=mocker.MagicMock(admin_username="admin", admin_password="secret"),
            )
            service = AuthService()
            result = service._authenticate_local("admin", "secret")
            assert result is True, f"Expected True but got {result=}"

        def test_returns_false_for_wrong_password(self, mocker):
            """Return False when the password does not match.

            Given: Settings with admin_password='secret'
            When: Calling _authenticate_local('admin', 'wrongpassword')
            Then: Should return False
            """
            mocker.patch(
                "app.services.auth_service.get_settings",
                return_value=mocker.MagicMock(admin_username="admin", admin_password="secret"),
            )
            service = AuthService()
            result = service._authenticate_local("admin", "wrongpassword")
            assert result is False, f"Expected False but got {result=}"

        def test_returns_false_for_wrong_username(self, mocker):
            """Return False when the username does not match.

            Given: Settings with admin_username='admin'
            When: Calling _authenticate_local('hacker', 'secret')
            Then: Should return False
            """
            mocker.patch(
                "app.services.auth_service.get_settings",
                return_value=mocker.MagicMock(admin_username="admin", admin_password="secret"),
            )
            service = AuthService()
            result = service._authenticate_local("hacker", "secret")
            assert result is False, f"Expected False but got {result=}"

    class TestAuthenticateLdap:
        """Tests for _authenticate_ldap()."""

        def test_returns_false_when_ldap_server_not_configured(self, mocker):
            """Return False immediately when ldap_server setting is empty.

            Given: Settings with ldap_server=None (or empty string)
            When: Calling _authenticate_ldap(...)
            Then: Should return False without attempting to connect
            """
            mocker.patch(
                "app.services.auth_service.get_settings",
                return_value=mocker.MagicMock(ldap_server=""),
            )
            service = AuthService()
            result = service._authenticate_ldap("user", "pass")
            assert result is False, f"Expected False but got {result=}"

        def test_returns_true_on_successful_bind(self, mocker):
            """Return True when LDAP bind succeeds.

            Given: A configured LDAP server and a successful simple_bind_s call
            When: Calling _authenticate_ldap('cn=user', 'pass')
            Then: Should return True
            """
            mock_settings = mocker.MagicMock(
                ldap_server="ldap://ldap.example.com",
                ldap_base_dn="dc=example,dc=com",
            )
            mocker.patch("app.services.auth_service.get_settings", return_value=mock_settings)
            mock_conn = mocker.MagicMock()
            mock_conn.simple_bind_s.return_value = (97, [])
            mocker.patch("ldap.initialize", return_value=mock_conn)

            service = AuthService()
            result = service._authenticate_ldap("user", "pass")
            assert result is True, f"Expected True but got {result=}"

        def test_returns_false_on_ldap_error(self, mocker):
            """Return False when LDAP raises LDAPError.

            Given: A configured LDAP server that raises ldap.LDAPError on bind
            When: Calling _authenticate_ldap(...)
            Then: Should return False without propagating the exception
            """
            mock_settings = mocker.MagicMock(
                ldap_server="ldap://ldap.example.com",
                ldap_base_dn="dc=example,dc=com",
            )
            mocker.patch("app.services.auth_service.get_settings", return_value=mock_settings)
            mock_conn = mocker.MagicMock()
            mock_conn.simple_bind_s.side_effect = ldap.LDAPError({"desc": "Invalid credentials"})
            mocker.patch("ldap.initialize", return_value=mock_conn)

            service = AuthService()
            result = service._authenticate_ldap("user", "wrongpass")
            assert result is False, f"Expected False but got {result=}"

    class TestAuthenticate:
        """Tests for the public authenticate() entry point."""

        def test_returns_true_via_local_when_ldap_disabled(self, mocker):
            """Fall through to local auth and return True when LDAP is not configured.

            Given: No LDAP server, valid local admin credentials
            When: Calling authenticate('admin', 'secret')
            Then: Should return True via local authentication
            """
            mocker.patch(
                "app.services.auth_service.get_settings",
                return_value=mocker.MagicMock(
                    ldap_server="",
                    admin_username="admin",
                    admin_password="secret",
                ),
            )
            service = AuthService()
            result = service.authenticate("admin", "secret")
            assert result is True, f"Expected True but got {result=}"

        def test_returns_false_when_all_methods_fail(self, mocker):
            """Return False when both LDAP and local authentication fail.

            Given: No LDAP server and wrong local credentials
            When: Calling authenticate('admin', 'wrong')
            Then: Should return False
            """
            mocker.patch(
                "app.services.auth_service.get_settings",
                return_value=mocker.MagicMock(
                    ldap_server="",
                    admin_username="admin",
                    admin_password="secret",
                ),
            )
            service = AuthService()
            result = service.authenticate("admin", "wrong")
            assert result is False, f"Expected False but got {result=}"
