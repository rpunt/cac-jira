"""
Tests for the IssueShow command.
"""

import argparse
from unittest.mock import MagicMock, patch

import pytest

from cac_jira.commands.issue.show import IssueShow


def make_issue(priority="High"):
    issue = MagicMock()
    issue.id = "10001"
    issue.key = "TEST-1"
    issue.raw = {"key": "TEST-1", "fields": {"summary": "A bug"}}
    issue.fields.summary = "A bug"
    issue.fields.status.name = "To Do"
    issue.fields.issuetype.name = "Bug"
    if priority is None:
        issue.fields.priority = None
    else:
        issue.fields.priority.name = priority
    return issue


class TestIssueShow:
    @pytest.fixture
    def cmd(self):
        command = IssueShow()
        command.log = MagicMock()
        command.jira_client = MagicMock()
        return command

    @patch("cac_core.output.Output")
    def test_show_table(self, mock_output, cmd):
        cmd.jira_client.issue.return_value = make_issue()

        result = cmd._execute(argparse.Namespace(issue="TEST-1", output="table"))

        assert result == 0
        models = mock_output.return_value.print_models.call_args[0][0]
        assert len(models) == 1
        assert models[0].Key == "TEST-1"
        assert models[0].Priority == "High"

    @patch("cac_core.output.Output")
    def test_show_table_without_priority(self, mock_output, cmd):
        cmd.jira_client.issue.return_value = make_issue(priority=None)

        result = cmd._execute(argparse.Namespace(issue="TEST-1", output="table"))

        assert result == 0
        models = mock_output.return_value.print_models.call_args[0][0]
        assert models[0].Priority == "None"

    def test_show_json(self, cmd, capsys):
        cmd.jira_client.issue.return_value = make_issue()

        result = cmd._execute(argparse.Namespace(issue="TEST-1", output="json"))

        assert result == 0
        out = capsys.readouterr().out
        assert '"key": "TEST-1"' in out

    def test_show_not_found(self, cmd):
        cmd.jira_client.issue.side_effect = Exception("does not exist")

        result = cmd._execute(argparse.Namespace(issue="NOPE-1", output="table"))

        assert result == 1
        cmd.log.error.assert_called()

    def test_show_returns_none(self, cmd):
        """A falsy issue is handled without an AttributeError."""
        cmd.jira_client.issue.return_value = None

        result = cmd._execute(argparse.Namespace(issue="NOPE-1", output="table"))

        assert result == 1
        cmd.log.error.assert_called()
