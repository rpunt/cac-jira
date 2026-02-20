"""
Tests for JiraClient authentication methods.

This module tests the JiraClient class, focusing on:
- Basic auth connection
- PAT (Personal Access Token) connection
- Auth method parameter handling
"""

import pytest
from unittest.mock import patch, MagicMock

from cac_jira.core.client import JiraClient


class TestJiraClientAuth:
    """Test suite for JiraClient authentication."""

    @patch("cac_jira.core.client.jira.JIRA")
    def test_basic_auth_uses_basic_auth_param(self, mock_jira_class):
        """Test that basic auth passes basic_auth tuple to jira.JIRA."""
        client = JiraClient("jira.example.com", "user@example.com", "api-token-123")

        mock_jira_class.assert_called_once_with(
            "https://jira.example.com",
            basic_auth=("user@example.com", "api-token-123"),
        )

    @patch("cac_jira.core.client.jira.JIRA")
    def test_explicit_basic_auth_method(self, mock_jira_class):
        """Test that explicitly passing auth_method='basic' uses basic_auth."""
        client = JiraClient(
            "jira.example.com", "user@example.com", "api-token-123", auth_method="basic"
        )

        mock_jira_class.assert_called_once_with(
            "https://jira.example.com",
            basic_auth=("user@example.com", "api-token-123"),
        )

    @patch("cac_jira.core.client.jira.JIRA")
    def test_pat_auth_uses_token_auth_param(self, mock_jira_class):
        """Test that PAT auth passes token_auth to jira.JIRA."""
        client = JiraClient(
            "jira.example.com", None, "pat-token-456", auth_method="pat"
        )

        mock_jira_class.assert_called_once_with(
            "https://jira.example.com",
            token_auth="pat-token-456",
        )

    @patch("cac_jira.core.client.jira.JIRA")
    def test_pat_auth_does_not_pass_basic_auth(self, mock_jira_class):
        """Test that PAT auth does not include basic_auth in the call."""
        client = JiraClient(
            "jira.example.com", "user@example.com", "pat-token-456", auth_method="pat"
        )

        call_kwargs = mock_jira_class.call_args[1]
        assert "basic_auth" not in call_kwargs
        assert call_kwargs["token_auth"] == "pat-token-456"

    @patch("cac_jira.core.client.jira.JIRA")
    def test_basic_auth_does_not_pass_token_auth(self, mock_jira_class):
        """Test that basic auth does not include token_auth in the call."""
        client = JiraClient("jira.example.com", "user@example.com", "api-token-123")

        call_kwargs = mock_jira_class.call_args[1]
        assert "token_auth" not in call_kwargs
        assert call_kwargs["basic_auth"] == ("user@example.com", "api-token-123")

    @patch("cac_jira.core.client.jira.JIRA")
    def test_pat_auth_with_none_username(self, mock_jira_class):
        """Test that PAT auth works when username is None."""
        client = JiraClient(
            "jira.example.com", None, "pat-token-456", auth_method="pat"
        )

        assert client.username is None
        assert client.auth_method == "pat"
        mock_jira_class.assert_called_once()

    @patch("cac_jira.core.client.jira.JIRA")
    def test_server_gets_https_prefix(self, mock_jira_class):
        """Test that the server URL gets an https:// prefix."""
        client = JiraClient("jira.example.com", "user@example.com", "token")

        call_args = mock_jira_class.call_args[0]
        assert call_args[0] == "https://jira.example.com"

    @patch("cac_jira.core.client.jira.JIRA")
    def test_attributes_stored_correctly(self, mock_jira_class):
        """Test that constructor arguments are stored as instance attributes."""
        client = JiraClient(
            "jira.example.com", "user@example.com", "token-123", auth_method="pat"
        )

        assert client.server == "jira.example.com"
        assert client.username == "user@example.com"
        assert client.api_token == "token-123"
        assert client.auth_method == "pat"

    @patch("cac_jira.core.client.jira.JIRA")
    def test_connect_failure_raises(self, mock_jira_class):
        """Test that a connection failure propagates the exception."""
        mock_jira_class.side_effect = Exception("Connection refused")

        with pytest.raises(Exception, match="Connection refused"):
            JiraClient("jira.example.com", "user@example.com", "token")
