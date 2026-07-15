"""
Tests for the issue transition commands: begin, close, and block.

These all delegate to JiraIssueCommand._transition_to, so the tests exercise
transition matching, comment handling, not-found handling, and exit codes.
"""

import argparse
from unittest.mock import MagicMock

import pytest

from cac_jira.commands.issue.begin import IssueBegin
from cac_jira.commands.issue.block import IssueBlock
from cac_jira.commands.issue.close import IssueClose


def make_cmd(cls):
    command = cls()
    command.log = MagicMock()
    command.jira_client = MagicMock()
    return command


def make_issue():
    issue = MagicMock()
    issue.key = "TEST-1"
    return issue


class TestIssueBegin:
    @pytest.fixture
    def cmd(self):
        return make_cmd(IssueBegin)

    def test_begin_success(self, cmd):
        issue = make_issue()
        cmd.jira_client.issue.return_value = issue
        cmd.jira_client.transitions.return_value = [
            {"id": "31", "name": "In Progress"},
            {"id": "41", "name": "Done"},
        ]

        result = cmd.execute(argparse.Namespace(issue="TEST-1"))

        assert result == 0
        cmd.jira_client.transition_issue.assert_called_once_with(issue, "31")

    def test_begin_transition_not_available(self, cmd):
        cmd.jira_client.issue.return_value = make_issue()
        cmd.jira_client.transitions.return_value = [{"id": "41", "name": "Done"}]

        result = cmd.execute(argparse.Namespace(issue="TEST-1"))

        assert result == 1
        cmd.jira_client.transition_issue.assert_not_called()

    def test_begin_issue_not_found(self, cmd):
        cmd.jira_client.issue.return_value = None

        result = cmd.execute(argparse.Namespace(issue="TEST-1"))

        assert result == 1
        cmd.jira_client.transitions.assert_not_called()


class TestIssueClose:
    @pytest.fixture
    def cmd(self):
        return make_cmd(IssueClose)

    def test_close_with_comment(self, cmd):
        issue = make_issue()
        cmd.jira_client.issue.return_value = issue
        cmd.jira_client.transitions.return_value = [{"id": "41", "name": "Done"}]

        result = cmd.execute(argparse.Namespace(issue="TEST-1", comment="all fixed"))

        assert result == 0
        cmd.jira_client.transition_issue.assert_called_once_with(issue, "41")
        cmd.jira_client.add_comment.assert_called_once_with(issue, "all fixed")

    def test_close_without_comment(self, cmd):
        issue = make_issue()
        cmd.jira_client.issue.return_value = issue
        cmd.jira_client.transitions.return_value = [{"id": "41", "name": "Done"}]

        result = cmd.execute(argparse.Namespace(issue="TEST-1", comment=None))

        assert result == 0
        cmd.jira_client.add_comment.assert_not_called()

    def test_close_transition_not_available(self, cmd):
        cmd.jira_client.issue.return_value = make_issue()
        cmd.jira_client.transitions.return_value = [{"id": "31", "name": "In Progress"}]

        result = cmd.execute(argparse.Namespace(issue="TEST-1", comment=None))

        assert result == 1


class TestIssueBlock:
    @pytest.fixture
    def cmd(self):
        return make_cmd(IssueBlock)

    def test_block_success(self, cmd):
        issue = make_issue()
        cmd.jira_client.issue.return_value = issue
        cmd.jira_client.transitions.return_value = [{"id": "51", "name": "Blocked"}]

        result = cmd.execute(argparse.Namespace(issue="TEST-1", comment=None))

        assert result == 0
        cmd.jira_client.transition_issue.assert_called_once_with(issue, "51")

    def test_block_matching_is_case_insensitive(self, cmd):
        issue = make_issue()
        cmd.jira_client.issue.return_value = issue
        cmd.jira_client.transitions.return_value = [{"id": "51", "name": "BLOCKED"}]

        result = cmd.execute(argparse.Namespace(issue="TEST-1", comment=None))

        assert result == 0
        cmd.jira_client.transition_issue.assert_called_once_with(issue, "51")
