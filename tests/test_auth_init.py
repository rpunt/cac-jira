"""
Tests for module-level authentication initialization in cac_jira/__init__.py.

This module tests the auth branching logic at module init, including:
- Basic auth credential retrieval
- PAT credential retrieval
- Error handling for missing credentials
- Username requirements per auth method
"""

import sys
import pytest
from unittest.mock import patch, MagicMock


def _reimport_cac_jira():
    """Remove all cac_jira modules from sys.modules and reimport."""
    modules_to_remove = [k for k in sys.modules if k.startswith("cac_jira")]
    for mod in modules_to_remove:
        del sys.modules[mod]
    import cac_jira
    return cac_jira


def _cleanup_cac_jira():
    """Remove all cac_jira modules from sys.modules."""
    modules_to_remove = [k for k in sys.modules if k.startswith("cac_jira")]
    for mod in modules_to_remove:
        del sys.modules[mod]


def _make_config_mock(config_dict):
    """Create a mock Config that returns values from the given dict."""
    mock_config = MagicMock()
    mock_config.get.side_effect = lambda key, default=None: config_dict.get(key, default)
    mock_config.config_file = "/mock/config"
    return mock_config


def _make_cred_mock(return_value):
    """Create a mock CredentialManager with the given credential return value."""
    mock_cred = MagicMock()
    mock_cred.get_credential.return_value = return_value
    return mock_cred


class TestBasicAuthInit:
    """Test module initialization with basic auth."""

    def teardown_method(self):
        _cleanup_cac_jira()

    @patch("jira.JIRA")
    @patch("cac_core.credentialmanager.CredentialManager")
    @patch("cac_core.config.Config")
    @patch("cac_core.updatechecker.check_package_for_updates")
    def test_basic_auth_retrieves_credential_with_username(
        self, mock_update, mock_config_class, mock_cred_class, mock_jira
    ):
        """Test that basic auth uses username to retrieve the API token."""
        mock_config_class.return_value = _make_config_mock({
            "server": "jira.example.com",
            "auth_method": "basic",
            "username": "user@example.com",
        })
        mock_cred = _make_cred_mock("api-token-123")
        mock_cred_class.return_value = mock_cred

        _reimport_cac_jira()

        mock_cred.get_credential.assert_called_once_with(
            "user@example.com", "Jira API key"
        )

    @patch("jira.JIRA")
    @patch("cac_core.credentialmanager.CredentialManager")
    @patch("cac_core.config.Config")
    @patch("cac_core.updatechecker.check_package_for_updates")
    def test_basic_auth_creates_client_with_basic_method(
        self, mock_update, mock_config_class, mock_cred_class, mock_jira
    ):
        """Test that basic auth creates JiraClient with auth_method='basic'."""
        mock_config_class.return_value = _make_config_mock({
            "server": "jira.example.com",
            "auth_method": "basic",
            "username": "user@example.com",
        })
        mock_cred_class.return_value = _make_cred_mock("api-token-123")

        cac_jira = _reimport_cac_jira()

        assert cac_jira.JIRA_CLIENT.auth_method == "basic"
        assert cac_jira.JIRA_CLIENT.username == "user@example.com"

    @patch("jira.JIRA")
    @patch("cac_core.credentialmanager.CredentialManager")
    @patch("cac_core.config.Config")
    @patch("cac_core.updatechecker.check_package_for_updates")
    def test_basic_auth_passes_basic_auth_to_jira(
        self, mock_update, mock_config_class, mock_cred_class, mock_jira
    ):
        """Test that basic auth passes basic_auth tuple to jira.JIRA."""
        mock_config_class.return_value = _make_config_mock({
            "server": "jira.example.com",
            "auth_method": "basic",
            "username": "user@example.com",
        })
        mock_cred_class.return_value = _make_cred_mock("api-token-123")

        _reimport_cac_jira()

        mock_jira.assert_called_once_with(
            "https://jira.example.com",
            basic_auth=("user@example.com", "api-token-123"),
        )

    @patch("cac_core.credentialmanager.CredentialManager")
    @patch("cac_core.config.Config")
    @patch("cac_core.updatechecker.check_package_for_updates")
    def test_basic_auth_exits_on_missing_username(
        self, mock_update, mock_config_class, mock_cred_class
    ):
        """Test that basic auth exits when username is INVALID_DEFAULT."""
        mock_config_class.return_value = _make_config_mock({
            "server": "jira.example.com",
            "auth_method": "basic",
            "username": "INVALID_DEFAULT",
        })

        with pytest.raises(SystemExit):
            _reimport_cac_jira()

    @patch("cac_core.credentialmanager.CredentialManager")
    @patch("cac_core.config.Config")
    @patch("cac_core.updatechecker.check_package_for_updates")
    def test_basic_auth_exits_on_missing_token(
        self, mock_update, mock_config_class, mock_cred_class
    ):
        """Test that basic auth exits when API token is not found."""
        mock_config_class.return_value = _make_config_mock({
            "server": "jira.example.com",
            "auth_method": "basic",
            "username": "user@example.com",
        })
        mock_cred_class.return_value = _make_cred_mock(None)

        with pytest.raises(SystemExit):
            _reimport_cac_jira()


class TestPATAuthInit:
    """Test module initialization with PAT auth."""

    def teardown_method(self):
        _cleanup_cac_jira()

    @patch("jira.JIRA")
    @patch("cac_core.credentialmanager.CredentialManager")
    @patch("cac_core.config.Config")
    @patch("cac_core.updatechecker.check_package_for_updates")
    def test_pat_auth_retrieves_credential_with_pat_key(
        self, mock_update, mock_config_class, mock_cred_class, mock_jira
    ):
        """Test that PAT auth uses '_pat_token' key to retrieve the token."""
        mock_config_class.return_value = _make_config_mock({
            "server": "jira.example.com",
            "auth_method": "pat",
            "username": None,
        })
        mock_cred = _make_cred_mock("pat-token-456")
        mock_cred_class.return_value = mock_cred

        _reimport_cac_jira()

        mock_cred.get_credential.assert_called_once_with(
            "_pat_token", "Jira Personal Access Token"
        )

    @patch("jira.JIRA")
    @patch("cac_core.credentialmanager.CredentialManager")
    @patch("cac_core.config.Config")
    @patch("cac_core.updatechecker.check_package_for_updates")
    def test_pat_auth_creates_client_with_pat_method(
        self, mock_update, mock_config_class, mock_cred_class, mock_jira
    ):
        """Test that PAT auth creates JiraClient with auth_method='pat'."""
        mock_config_class.return_value = _make_config_mock({
            "server": "jira.example.com",
            "auth_method": "pat",
            "username": None,
        })
        mock_cred_class.return_value = _make_cred_mock("pat-token-456")

        cac_jira = _reimport_cac_jira()

        assert cac_jira.JIRA_CLIENT.auth_method == "pat"

    @patch("jira.JIRA")
    @patch("cac_core.credentialmanager.CredentialManager")
    @patch("cac_core.config.Config")
    @patch("cac_core.updatechecker.check_package_for_updates")
    def test_pat_auth_passes_token_auth_to_jira(
        self, mock_update, mock_config_class, mock_cred_class, mock_jira
    ):
        """Test that PAT auth passes token_auth to jira.JIRA."""
        mock_config_class.return_value = _make_config_mock({
            "server": "jira.example.com",
            "auth_method": "pat",
            "username": None,
        })
        mock_cred_class.return_value = _make_cred_mock("pat-token-456")

        _reimport_cac_jira()

        mock_jira.assert_called_once_with(
            "https://jira.example.com",
            token_auth="pat-token-456",
        )

    @patch("jira.JIRA")
    @patch("cac_core.credentialmanager.CredentialManager")
    @patch("cac_core.config.Config")
    @patch("cac_core.updatechecker.check_package_for_updates")
    def test_pat_auth_does_not_require_username(
        self, mock_update, mock_config_class, mock_cred_class, mock_jira
    ):
        """Test that PAT auth works without a username configured."""
        mock_config_class.return_value = _make_config_mock({
            "server": "jira.example.com",
            "auth_method": "pat",
        })
        mock_cred_class.return_value = _make_cred_mock("pat-token-456")

        cac_jira = _reimport_cac_jira()

        # Should not exit — username is optional for PAT
        assert cac_jira.JIRA_CLIENT.username is None

    @patch("cac_core.credentialmanager.CredentialManager")
    @patch("cac_core.config.Config")
    @patch("cac_core.updatechecker.check_package_for_updates")
    def test_pat_auth_exits_on_missing_token(
        self, mock_update, mock_config_class, mock_cred_class
    ):
        """Test that PAT auth exits when token is not found."""
        mock_config_class.return_value = _make_config_mock({
            "server": "jira.example.com",
            "auth_method": "pat",
            "username": None,
        })
        mock_cred_class.return_value = _make_cred_mock(None)

        with pytest.raises(SystemExit):
            _reimport_cac_jira()


class TestDefaultAuthMethod:
    """Test that auth_method defaults to 'basic' when not configured."""

    def teardown_method(self):
        _cleanup_cac_jira()

    @patch("jira.JIRA")
    @patch("cac_core.credentialmanager.CredentialManager")
    @patch("cac_core.config.Config")
    @patch("cac_core.updatechecker.check_package_for_updates")
    def test_defaults_to_basic_when_auth_method_not_set(
        self, mock_update, mock_config_class, mock_cred_class, mock_jira
    ):
        """Test that omitting auth_method from config defaults to basic auth."""
        mock_config_class.return_value = _make_config_mock({
            "server": "jira.example.com",
            "username": "user@example.com",
        })
        mock_cred_class.return_value = _make_cred_mock("api-token-123")

        cac_jira = _reimport_cac_jira()

        assert cac_jira.JIRA_CLIENT.auth_method == "basic"
        mock_jira.assert_called_once_with(
            "https://jira.example.com",
            basic_auth=("user@example.com", "api-token-123"),
        )
