"""
Tests for the IssueCreate command.
"""

import argparse
from unittest.mock import MagicMock, patch

import pytest

from cac_jira.commands.issue.create import IssueCreate


def make_issuetype(name):
    it = MagicMock()
    it.name = name
    return it


def make_args(**kwargs):
    defaults = {
        "project": "TEST",
        "title": "Test Issue",
        "description": "Test description",
        "type": "Task",
        "assign": False,
        "begin": False,
        "epic": None,
        "labels": None,
        "epic_name": None,
        "browse": False,
        "custom_fields": None,
        "output": "table",
        "verbose": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


@pytest.fixture
def cmd():
    command = IssueCreate()
    command.log = MagicMock()
    command.jira_client = MagicMock()

    mock_project = MagicMock()
    mock_project.key = "TEST"
    mock_project.issueTypes = [make_issuetype("Task"), make_issuetype("Bug")]

    command.jira_client.project.return_value = mock_project
    command.jira_client.current_user.return_value = "user-account-id"
    command.jira_client.createmeta.return_value = {
        "projects": [{"issuetypes": [{"fields": {}}]}]
    }

    mock_issue = MagicMock()
    mock_issue.key = "TEST-1"
    mock_issue.permalink.return_value = "https://test.atlassian.net/browse/TEST-1"
    command.jira_client.create_issue.return_value = mock_issue

    return command


class TestIssueCreateValidation:
    def test_missing_project(self, cmd):
        result = cmd.execute(make_args(project=None))
        assert result == 1
        cmd.log.error.assert_called()

    def test_project_not_found(self, cmd):
        cmd.jira_client.project.side_effect = Exception("Not found")
        result = cmd.execute(make_args())
        assert result == 1
        cmd.log.error.assert_called()

    def test_invalid_issue_type(self, cmd):
        result = cmd.execute(make_args(type="InvalidType"))
        assert result == 1
        cmd.log.error.assert_called()
        error_msg = cmd.log.error.call_args[0][0]
        assert "Invalid issue type" in error_msg

    def test_valid_issue_type_case_insensitive(self, cmd):
        cmd.execute(make_args(type="task"))
        cmd.jira_client.create_issue.assert_called_once()


class TestIssueCreateExecution:
    def test_successful_creation(self, cmd):
        cmd.execute(make_args())
        cmd.jira_client.create_issue.assert_called_once()
        fields = cmd.jira_client.create_issue.call_args[1]["fields"]
        assert fields["project"] == "TEST"
        assert fields["summary"] == "Test Issue"
        assert fields["description"] == "Test description"
        assert fields["issuetype"] == {"name": "Task"}

    def test_creation_with_labels(self, cmd):
        cmd.execute(make_args(labels="bug,urgent"))
        fields = cmd.jira_client.create_issue.call_args[1]["fields"]
        assert fields["labels"] == ["bug", "urgent"]

    def test_creation_with_epic(self, cmd):
        mock_epic = MagicMock()
        mock_epic.key = "TEST-99"
        cmd.jira_client.issue.return_value = mock_epic
        cmd.execute(make_args(epic="TEST-99"))
        fields = cmd.jira_client.create_issue.call_args[1]["fields"]
        assert fields["parent"] == {"key": "TEST-99"}

    def test_creation_with_assign(self, cmd):
        cmd.execute(make_args(assign=True))
        created_issue = cmd.jira_client.create_issue.return_value
        created_issue.update.assert_called_once_with(
            assignee={"accountId": "user-account-id"}
        )

    def test_begin_implies_assign(self, cmd):
        with patch("cac_jira.commands.issue.begin.IssueBegin") as mock_begin_cls:
            mock_begin_cls.return_value.execute = MagicMock()
            cmd.execute(make_args(begin=True))
        created_issue = cmd.jira_client.create_issue.return_value
        created_issue.update.assert_called_once_with(
            assignee={"accountId": "user-account-id"}
        )

    def test_begin_triggers_transition(self, cmd):
        with patch("cac_jira.commands.issue.begin.IssueBegin") as mock_begin_cls:
            mock_begin_instance = MagicMock()
            mock_begin_cls.return_value = mock_begin_instance
            cmd.execute(make_args(begin=True))
        mock_begin_instance.execute.assert_called_once()
        begin_args = mock_begin_instance.execute.call_args[0][0]
        assert begin_args.issue == "TEST-1"

    def test_browse_opens_url(self, cmd):
        with patch("webbrowser.open") as mock_open:
            cmd.execute(make_args(browse=True))
        mock_open.assert_called_once_with("https://test.atlassian.net/browse/TEST-1")
