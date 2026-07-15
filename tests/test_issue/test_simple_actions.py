"""
Tests for the simple pass-through issue commands: comment, assign, label, browse.
"""

import argparse
from unittest.mock import MagicMock, patch

import pytest

from cac_jira.commands.issue.assign import IssueAssign
from cac_jira.commands.issue.browse import IssueBrowse
from cac_jira.commands.issue.comment import IssueComment
from cac_jira.commands.issue.label import IssueLabel


def make_cmd(cls):
    command = cls()
    command.log = MagicMock()
    command.jira_client = MagicMock()
    return command


class TestIssueComment:
    @pytest.fixture
    def cmd(self):
        return make_cmd(IssueComment)

    def test_comment(self, cmd):
        result = cmd._execute(argparse.Namespace(issue="TEST-1", comment="hello"))

        assert result == 0
        cmd.jira_client.add_comment.assert_called_once_with("TEST-1", "hello")

    def test_comment_error(self, cmd):
        cmd.jira_client.add_comment.side_effect = Exception("boom")

        result = cmd._execute(argparse.Namespace(issue="TEST-1", comment="hello"))

        assert result == 1
        cmd.log.error.assert_called()


class TestIssueAssign:
    @pytest.fixture
    def cmd(self):
        command = make_cmd(IssueAssign)
        command.config = MagicMock(username="me@example.com")
        return command

    def test_assign_to_self(self, cmd):
        result = cmd._execute(argparse.Namespace(issue="TEST-1"))

        assert result == 0
        cmd.jira_client.assign_issue.assert_called_once_with("TEST-1", "me@example.com")

    def test_assign_error(self, cmd):
        cmd.jira_client.assign_issue.side_effect = Exception("boom")

        result = cmd._execute(argparse.Namespace(issue="TEST-1"))

        assert result == 1
        cmd.log.error.assert_called()


class TestIssueLabel:
    @pytest.fixture
    def cmd(self):
        return make_cmd(IssueLabel)

    def test_label(self, cmd):
        result = cmd._execute(argparse.Namespace(issue="TEST-1", labels="bug,urgent"))

        assert result == 0
        cmd.jira_client.add_labels.assert_called_once_with("TEST-1", "bug,urgent")

    def test_label_rejects_invalid(self, cmd):
        """Invalid input surfaces as a ValueError from the client -> exit 1."""
        cmd.jira_client.add_labels.side_effect = ValueError("No valid labels provided")

        result = cmd._execute(argparse.Namespace(issue="TEST-1", labels=" , "))

        assert result == 1
        cmd.log.info.assert_not_called()

    def test_label_update_error(self, cmd):
        cmd.jira_client.add_labels.side_effect = Exception("boom")

        result = cmd._execute(argparse.Namespace(issue="TEST-1", labels="bug"))

        assert result == 1
        cmd.log.error.assert_called()
        cmd.log.info.assert_not_called()


class TestIssueBrowse:
    @pytest.fixture
    def cmd(self):
        return make_cmd(IssueBrowse)

    def test_browse_opens_permalink(self, cmd):
        issue = MagicMock()
        issue.permalink.return_value = "https://test.atlassian.net/browse/TEST-1"
        cmd.jira_client.issue.return_value = issue

        with patch("webbrowser.open") as mock_open:
            result = cmd._execute(argparse.Namespace(issue="TEST-1"))

        assert result == 0
        mock_open.assert_called_once_with("https://test.atlassian.net/browse/TEST-1")

    def test_browse_lookup_error(self, cmd):
        cmd.jira_client.issue.side_effect = Exception("does not exist")

        with patch("webbrowser.open") as mock_open:
            result = cmd._execute(argparse.Namespace(issue="TEST-1"))

        assert result == 1
        mock_open.assert_not_called()
        cmd.log.error.assert_called()

    def test_browse_issue_none(self, cmd):
        cmd.jira_client.issue.return_value = None

        with patch("webbrowser.open") as mock_open:
            result = cmd._execute(argparse.Namespace(issue="TEST-1"))

        assert result == 1
        mock_open.assert_not_called()
        cmd.log.error.assert_called()
