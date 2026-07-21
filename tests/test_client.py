"""
Tests for JiraClient authentication handling.
"""

from typing import cast
from unittest.mock import MagicMock, patch

import pytest
from jira.exceptions import JIRAError

from cac_jira.core.client import JiraAuthenticationError, JiraClient


def _make_auth_failure():
    """Create a JIRAError that simulates Jira's auth-failed-as-404 response."""
    response = MagicMock()
    response.headers = {"X-Seraph-Loginreason": "AUTHENTICATED_FAILED"}
    return JIRAError(
        status_code=404,
        text="No project could be found with key 'TEST'.",
        response=response,
    )


@patch("jira.JIRA")
class TestJiraClientAuth:
    def test_auth_failure_raises_authentication_error(self, mock_jira_class):
        mock_client = MagicMock()
        mock_client.myself.side_effect = _make_auth_failure()
        mock_jira_class.return_value = mock_client

        with pytest.raises(JiraAuthenticationError, match="API token may be invalid"):
            JiraClient("test.atlassian.net", "user@example.com", "bad-token")

    def test_non_auth_jira_error_propagates(self, mock_jira_class):
        mock_client = MagicMock()
        response = MagicMock()
        response.headers = {"X-Seraph-Loginreason": "OK"}
        mock_client.myself.side_effect = JIRAError(
            status_code=500, text="Server error", response=response
        )
        mock_jira_class.return_value = mock_client

        with pytest.raises(JIRAError):
            JiraClient("test.atlassian.net", "user@example.com", "token")

    def test_successful_connect(self, mock_jira_class):
        mock_client = MagicMock()
        mock_client.myself.return_value = {"accountId": "123"}
        mock_jira_class.return_value = mock_client

        client = JiraClient("test.atlassian.net", "user@example.com", "good-token")

        assert client.client is mock_client
        mock_client.myself.assert_called_once()


@patch("jira.JIRA")
class TestJiraClientAddLabels:
    def _client(self, mock_jira_class):
        mock_client = MagicMock()
        mock_client.myself.return_value = {"accountId": "123"}
        mock_jira_class.return_value = mock_client
        return JiraClient("test.atlassian.net", "user@example.com", "token")

    def test_add_labels_success_preserves_and_strips(self, mock_jira_class):
        client = self._client(mock_jira_class)
        issue = MagicMock()
        cast(MagicMock, client.client).issue.return_value = issue

        result = client.add_labels("TEST-1", "a, b")

        # Uses the "add" verb (preserving existing labels) and strips whitespace.
        issue.update.assert_called_once_with(
            update={"labels": [{"add": "a"}, {"add": "b"}]}
        )
        assert result is issue.update.return_value

    def test_add_labels_empty_raises_value_error(self, mock_jira_class):
        client = self._client(mock_jira_class)

        with pytest.raises(ValueError):
            client.add_labels("TEST-1", " , ")
        # Validation happens before any lookup/update is attempted.
        cast(MagicMock, client.client).issue.assert_not_called()

    def test_add_labels_lookup_error_propagates(self, mock_jira_class):
        client = self._client(mock_jira_class)
        cast(MagicMock, client.client).issue.side_effect = JIRAError(
            status_code=404, text="nope"
        )

        with pytest.raises(JIRAError):
            client.add_labels("TEST-1", "bug")


@patch("jira.JIRA")
class TestJiraClientAuthMethods:
    """The auth_method flag selects basic_auth vs token_auth at connect time."""

    def test_basic_auth_uses_basic_auth_param(self, mock_jira_class):
        JiraClient("jira.example.com", "user@example.com", "api-token-123")

        mock_jira_class.assert_called_once_with(
            "https://jira.example.com",
            basic_auth=("user@example.com", "api-token-123"),
        )

    def test_pat_auth_uses_token_auth_param(self, mock_jira_class):
        JiraClient("jira.example.com", None, "pat-token-456", auth_method="pat")

        mock_jira_class.assert_called_once_with(
            "https://jira.example.com",
            token_auth="pat-token-456",
        )

    def test_pat_auth_omits_basic_auth(self, mock_jira_class):
        JiraClient(
            "jira.example.com",
            "user@example.com",
            "pat-token-456",
            auth_method="pat",
        )

        call_kwargs = mock_jira_class.call_args[1]
        assert "basic_auth" not in call_kwargs
        assert call_kwargs["token_auth"] == "pat-token-456"

    def test_auth_method_and_username_stored(self, mock_jira_class):
        client = JiraClient("jira.example.com", None, "pat-token", auth_method="pat")

        assert client.auth_method == "pat"
        assert client.username is None

    def test_auth_method_is_normalized(self, mock_jira_class):
        # A case/whitespace-variant PAT value must still select token_auth.
        client = JiraClient("jira.example.com", None, "pat-token", auth_method=" PAT ")

        assert client.auth_method == "pat"
        mock_jira_class.assert_called_once_with(
            "https://jira.example.com",
            token_auth="pat-token",
        )

    def test_none_auth_method_defaults_to_basic(self, mock_jira_class):
        client = JiraClient(
            "jira.example.com", "user@example.com", "api-token", auth_method=None
        )

        assert client.auth_method == "basic"

    def test_basic_auth_requires_username(self, mock_jira_class):
        with pytest.raises(ValueError, match="username is required"):
            JiraClient("jira.example.com", None, "api-token")

    def test_missing_token_raises(self, mock_jira_class):
        with pytest.raises(ValueError, match="token is required"):
            JiraClient("jira.example.com", "user@example.com", None)
