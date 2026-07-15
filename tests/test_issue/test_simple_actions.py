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
        result = cmd.execute(argparse.Namespace(issue="TEST-1", comment="hello"))

        assert result == 0
        cmd.jira_client.add_comment.assert_called_once_with("TEST-1", "hello")


class TestIssueAssign:
    @pytest.fixture
    def cmd(self):
        command = make_cmd(IssueAssign)
        command.config = MagicMock(username="me@example.com")
        return command

    def test_assign_to_self(self, cmd):
        result = cmd.execute(argparse.Namespace(issue="TEST-1"))

        assert result == 0
        cmd.jira_client.assign_issue.assert_called_once_with("TEST-1", "me@example.com")


class TestIssueLabel:
    @pytest.fixture
    def cmd(self):
        return make_cmd(IssueLabel)

    def test_label(self, cmd):
        result = cmd.execute(argparse.Namespace(issue="TEST-1", labels="bug,urgent"))

        assert result == 0
        cmd.jira_client.add_labels.assert_called_once_with("TEST-1", "bug,urgent")

    def test_label_rejects_empty(self, cmd):
        result = cmd.execute(argparse.Namespace(issue="TEST-1", labels=" , "))

        assert result == 1
        cmd.jira_client.add_labels.assert_not_called()


class TestIssueBrowse:
    @pytest.fixture
    def cmd(self):
        return make_cmd(IssueBrowse)

    def test_browse_opens_permalink(self, cmd):
        issue = MagicMock()
        issue.permalink.return_value = "https://test.atlassian.net/browse/TEST-1"
        cmd.jira_client.issue.return_value = issue

        with patch("webbrowser.open") as mock_open:
            result = cmd.execute(argparse.Namespace(issue="TEST-1"))

        assert result == 0
        mock_open.assert_called_once_with("https://test.atlassian.net/browse/TEST-1")
