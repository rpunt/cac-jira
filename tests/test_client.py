"""
Tests for JiraClient authentication handling.
"""

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
