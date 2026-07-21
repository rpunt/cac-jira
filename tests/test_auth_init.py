"""
Tests for auth-method branching during module initialization.

These exercise ``cac_jira._initialize_config`` / ``_initialize_client`` with the
config, credential manager, update checker, and jira client all mocked, so the
basic-vs-PAT logic is tested in isolation from the network and the filesystem.
"""

from unittest.mock import MagicMock, patch

import pytest


def _reimport_cac_jira():
    """Reset cac_jira's lazy state and re-run initialization.

    State is reset in place rather than deleting the module from ``sys.modules``
    so that other test modules (which imported command classes from cac_jira at
    collection time) keep working — a fresh reimport would leave them bound to a
    stale module object.
    """
    import cac_jira

    cac_jira._module_state.clear()
    cac_jira._initialized = False
    cac_jira._initialize()
    return cac_jira


def _cleanup_cac_jira():
    import cac_jira

    cac_jira._module_state.clear()
    cac_jira._initialized = False


def _make_config_mock(config_dict):
    """A mock Config whose ``get`` reads from ``config_dict``."""
    config_dict.setdefault("project", "TEST")
    mock_config = MagicMock()
    mock_config.get.side_effect = lambda key, default=None: config_dict.get(
        key, default
    )
    mock_config.config_file = "/mock/config"
    return mock_config


def _make_cred_mock(return_value):
    mock_cred = MagicMock()
    mock_cred.get_credential.return_value = return_value
    return mock_cred


def _ensure_keys_names(mock_config):
    """The key names passed to ``config.ensure_keys`` during init."""
    keys = mock_config.ensure_keys.call_args[0][0]
    return [entry[0] for entry in keys]


class TestBasicAuthInit:
    def teardown_method(self):
        _cleanup_cac_jira()

    @patch("jira.JIRA")
    @patch("cac_core.credentialmanager.CredentialManager")
    @patch("cac_core.config.Config")
    @patch("cac_core.updatechecker.check_package_for_updates")
    def test_retrieves_credential_with_username(
        self, _mock_update, mock_config_class, mock_cred_class, _mock_jira
    ):
        mock_config_class.return_value = _make_config_mock(
            {
                "server": "jira.example.com",
                "auth_method": "basic",
                "username": "user@example.com",
            }
        )
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
    def test_creates_client_with_basic_method(
        self, _mock_update, mock_config_class, mock_cred_class, _mock_jira
    ):
        mock_config_class.return_value = _make_config_mock(
            {
                "server": "jira.example.com",
                "auth_method": "basic",
                "username": "user@example.com",
            }
        )
        mock_cred_class.return_value = _make_cred_mock("api-token-123")

        cac_jira = _reimport_cac_jira()

        assert cac_jira.JIRA_CLIENT.auth_method == "basic"
        assert cac_jira.JIRA_CLIENT.username == "user@example.com"

    @patch("jira.JIRA")
    @patch("cac_core.credentialmanager.CredentialManager")
    @patch("cac_core.config.Config")
    @patch("cac_core.updatechecker.check_package_for_updates")
    def test_passes_basic_auth_to_jira(
        self, _mock_update, mock_config_class, mock_cred_class, mock_jira
    ):
        mock_config_class.return_value = _make_config_mock(
            {
                "server": "jira.example.com",
                "auth_method": "basic",
                "username": "user@example.com",
            }
        )
        mock_cred_class.return_value = _make_cred_mock("api-token-123")

        _reimport_cac_jira()

        mock_jira.assert_called_once_with(
            "https://jira.example.com",
            basic_auth=("user@example.com", "api-token-123"),
        )

    @patch("jira.JIRA")
    @patch("cac_core.credentialmanager.CredentialManager")
    @patch("cac_core.config.Config")
    @patch("cac_core.updatechecker.check_package_for_updates")
    def test_username_is_prompted(
        self, _mock_update, mock_config_class, mock_cred_class, _mock_jira
    ):
        mock_config = _make_config_mock(
            {
                "server": "jira.example.com",
                "auth_method": "basic",
                "username": "user@example.com",
            }
        )
        mock_config_class.return_value = mock_config
        mock_cred_class.return_value = _make_cred_mock("api-token-123")

        _reimport_cac_jira()

        # Basic auth includes username in the first-run prompts.
        assert "username" in _ensure_keys_names(mock_config)

    @patch("cac_core.credentialmanager.CredentialManager")
    @patch("cac_core.config.Config")
    @patch("cac_core.updatechecker.check_package_for_updates")
    def test_exits_on_missing_token(
        self, _mock_update, mock_config_class, mock_cred_class
    ):
        mock_config_class.return_value = _make_config_mock(
            {
                "server": "jira.example.com",
                "auth_method": "basic",
                "username": "user@example.com",
            }
        )
        mock_cred_class.return_value = _make_cred_mock(None)

        with pytest.raises(SystemExit):
            _reimport_cac_jira()


class TestPATAuthInit:
    def teardown_method(self):
        _cleanup_cac_jira()

    @patch("jira.JIRA")
    @patch("cac_core.credentialmanager.CredentialManager")
    @patch("cac_core.config.Config")
    @patch("cac_core.updatechecker.check_package_for_updates")
    def test_retrieves_credential_with_pat_key(
        self, _mock_update, mock_config_class, mock_cred_class, _mock_jira
    ):
        mock_config_class.return_value = _make_config_mock(
            {"server": "jira.example.com", "auth_method": "pat", "username": None}
        )
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
    def test_creates_client_with_pat_method(
        self, _mock_update, mock_config_class, mock_cred_class, _mock_jira
    ):
        mock_config_class.return_value = _make_config_mock(
            {"server": "jira.example.com", "auth_method": "pat", "username": None}
        )
        mock_cred_class.return_value = _make_cred_mock("pat-token-456")

        cac_jira = _reimport_cac_jira()

        assert cac_jira.JIRA_CLIENT.auth_method == "pat"

    @patch("jira.JIRA")
    @patch("cac_core.credentialmanager.CredentialManager")
    @patch("cac_core.config.Config")
    @patch("cac_core.updatechecker.check_package_for_updates")
    def test_passes_token_auth_to_jira(
        self, _mock_update, mock_config_class, mock_cred_class, mock_jira
    ):
        mock_config_class.return_value = _make_config_mock(
            {"server": "jira.example.com", "auth_method": "pat", "username": None}
        )
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
    def test_username_not_prompted(
        self, _mock_update, mock_config_class, mock_cred_class, _mock_jira
    ):
        mock_config = _make_config_mock(
            {"server": "jira.example.com", "auth_method": "pat"}
        )
        mock_config_class.return_value = mock_config
        mock_cred_class.return_value = _make_cred_mock("pat-token-456")

        cac_jira = _reimport_cac_jira()

        # PAT does not require a username, so it is left out of the prompts.
        assert "username" not in _ensure_keys_names(mock_config)
        assert cac_jira.JIRA_CLIENT.username is None

    @patch("cac_core.credentialmanager.CredentialManager")
    @patch("cac_core.config.Config")
    @patch("cac_core.updatechecker.check_package_for_updates")
    def test_exits_on_missing_token(
        self, _mock_update, mock_config_class, mock_cred_class
    ):
        mock_config_class.return_value = _make_config_mock(
            {"server": "jira.example.com", "auth_method": "pat", "username": None}
        )
        mock_cred_class.return_value = _make_cred_mock(None)

        with pytest.raises(SystemExit):
            _reimport_cac_jira()


class TestDefaultAuthMethod:
    def teardown_method(self):
        _cleanup_cac_jira()

    @patch("jira.JIRA")
    @patch("cac_core.credentialmanager.CredentialManager")
    @patch("cac_core.config.Config")
    @patch("cac_core.updatechecker.check_package_for_updates")
    def test_defaults_to_basic_when_unset(
        self, _mock_update, mock_config_class, mock_cred_class, mock_jira
    ):
        mock_config_class.return_value = _make_config_mock(
            {"server": "jira.example.com", "username": "user@example.com"}
        )
        mock_cred_class.return_value = _make_cred_mock("api-token-123")

        cac_jira = _reimport_cac_jira()

        assert cac_jira.JIRA_CLIENT.auth_method == "basic"
        mock_jira.assert_called_once_with(
            "https://jira.example.com",
            basic_auth=("user@example.com", "api-token-123"),
        )
