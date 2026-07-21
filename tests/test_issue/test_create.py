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
        result = cmd.run(make_args(project=None))
        assert result == 1
        cmd.log.error.assert_called()

    def test_project_not_found(self, cmd):
        cmd.jira_client.project.side_effect = Exception("Not found")
        result = cmd.run(make_args())
        assert result == 1
        cmd.log.error.assert_called()

    def test_invalid_issue_type(self, cmd):
        result = cmd.run(make_args(type="InvalidType"))
        assert result == 1
        cmd.log.error.assert_called()
        error_msg = cmd.log.error.call_args[0][0]
        assert "Invalid issue type" in error_msg

    def test_valid_issue_type_case_insensitive(self, cmd):
        cmd.run(make_args(type="task"))
        cmd.jira_client.create_issue.assert_called_once()


class TestIssueCreateExecution:
    def test_successful_creation(self, cmd):
        cmd.run(make_args())
        cmd.jira_client.create_issue.assert_called_once()
        fields = cmd.jira_client.create_issue.call_args[1]["fields"]
        assert fields["project"] == "TEST"
        assert fields["summary"] == "Test Issue"
        assert fields["description"] == "Test description"
        assert fields["issuetype"] == {"name": "Task"}

    def test_creation_with_labels(self, cmd):
        cmd.run(make_args(labels="bug,urgent"))
        fields = cmd.jira_client.create_issue.call_args[1]["fields"]
        assert fields["labels"] == ["bug", "urgent"]

    def test_creation_with_epic(self, cmd):
        mock_epic = MagicMock()
        mock_epic.key = "TEST-99"
        cmd.jira_client.issue.return_value = mock_epic
        cmd.run(make_args(epic="TEST-99"))
        fields = cmd.jira_client.create_issue.call_args[1]["fields"]
        assert fields["parent"] == {"key": "TEST-99"}

    def test_creation_epic_not_found(self, cmd):
        cmd.jira_client.issue.side_effect = Exception("no such epic")
        result = cmd.run(make_args(epic="TEST-99"))
        assert result == 1
        cmd.jira_client.create_issue.assert_not_called()

    def test_creation_with_assign(self, cmd):
        cmd.run(make_args(assign=True))
        created_issue = cmd.jira_client.create_issue.return_value
        created_issue.update.assert_called_once_with(
            assignee={"accountId": "user-account-id"}
        )

    def test_begin_implies_assign(self, cmd):
        with patch("cac_jira.commands.issue.begin.IssueBegin") as mock_begin_cls:
            mock_begin_cls.return_value.run = MagicMock(return_value=0)
            cmd.run(make_args(begin=True))
        created_issue = cmd.jira_client.create_issue.return_value
        created_issue.update.assert_called_once_with(
            assignee={"accountId": "user-account-id"}
        )

    def test_begin_triggers_transition(self, cmd):
        with patch("cac_jira.commands.issue.begin.IssueBegin") as mock_begin_cls:
            mock_begin_instance = MagicMock()
            mock_begin_instance.run.return_value = 0
            mock_begin_cls.return_value = mock_begin_instance
            cmd.run(make_args(begin=True))
        mock_begin_instance.run.assert_called_once()
        begin_args = mock_begin_instance.run.call_args[0][0]
        assert begin_args.issue == "TEST-1"

    def test_begin_failure_propagates(self, cmd):
        """If the begin transition fails, create surfaces the non-zero code."""
        with patch("cac_jira.commands.issue.begin.IssueBegin") as mock_begin_cls:
            mock_begin_cls.return_value.run.return_value = 1
            result = cmd.run(make_args(begin=True))
        assert result == 1

    def test_browse_opens_url(self, cmd):
        with patch("webbrowser.open") as mock_open:
            cmd.run(make_args(browse=True))
        mock_open.assert_called_once_with("https://test.atlassian.net/browse/TEST-1")


def _createmeta(fields):
    """Wrap a fields dict in the createmeta response shape."""
    return {"projects": [{"issuetypes": [{"fields": fields}]}]}


class TestIssueCreateMandatoryFields:
    """get_mandatory_fields parsing and the --field / missing-field handling."""

    def test_get_mandatory_fields_parses_required_only(self, cmd):
        cmd.jira_client.createmeta.return_value = _createmeta(
            {
                "customfield_1": {
                    "name": "Points",
                    "required": True,
                    "schema": {"type": "number"},
                },
                "customfield_2": {"name": "Optional", "required": False},
            }
        )
        result = cmd.get_mandatory_fields("TEST", "Task")
        assert "customfield_1" in result
        assert "customfield_2" not in result
        assert result["customfield_1"]["name"] == "Points"

    def test_get_mandatory_fields_bad_metadata_returns_empty(self, cmd):
        cmd.jira_client.createmeta.return_value = {"projects": []}  # IndexError
        assert cmd.get_mandatory_fields("TEST", "Task") == {}
        cmd.log.error.assert_called()

    def test_custom_field_mapped_by_name(self, cmd):
        cmd.jira_client.createmeta.return_value = _createmeta(
            {
                "customfield_101": {
                    "name": "Story Points",
                    "required": True,
                    "schema": {"type": "number"},
                }
            }
        )
        cmd.run(make_args(custom_fields=[["Story Points", "5"]]))
        fields = cmd.jira_client.create_issue.call_args.kwargs["fields"]
        # Name resolved to the field id, value passed through.
        assert fields["customfield_101"] == "5"

    def test_custom_field_array_type_split(self, cmd):
        cmd.jira_client.createmeta.return_value = _createmeta(
            {
                "customfield_200": {
                    "name": "Components",
                    "required": True,
                    "schema": {"type": "array"},
                }
            }
        )
        cmd.run(make_args(custom_fields=[["customfield_200", "a,b,c"]]))
        fields = cmd.jira_client.create_issue.call_args.kwargs["fields"]
        assert fields["customfield_200"] == ["a", "b", "c"]

    def test_custom_field_option_type_wrapped(self, cmd):
        cmd.jira_client.createmeta.return_value = _createmeta(
            {
                "customfield_300": {
                    "name": "Severity",
                    "required": True,
                    "schema": {"type": "option"},
                }
            }
        )
        cmd.run(make_args(custom_fields=[["customfield_300", "High"]]))
        fields = cmd.jira_client.create_issue.call_args.kwargs["fields"]
        assert fields["customfield_300"] == {"value": "High"}

    def test_custom_field_non_customfield_id_passthrough(self, cmd):
        cmd.jira_client.createmeta.return_value = _createmeta(
            {"duedate": {"name": "Due Date", "required": True, "schema": {}}}
        )
        cmd.run(make_args(custom_fields=[["duedate", "2026-01-01"]]))
        fields = cmd.jira_client.create_issue.call_args.kwargs["fields"]
        assert fields["duedate"] == "2026-01-01"

    def test_missing_mandatory_field_fails(self, cmd):
        cmd.jira_client.createmeta.return_value = _createmeta(
            {"customfield_999": {"name": "Required Thing", "required": True}}
        )
        # No --field supplied -> ValueError in execute -> run() maps to exit 1.
        assert cmd.run(make_args()) == 1
        cmd.jira_client.create_issue.assert_not_called()

    def test_builtin_mandatory_fields_not_flagged(self, cmd):
        # A required field the command already supplies (summary) must not be
        # reported as missing.
        cmd.jira_client.createmeta.return_value = _createmeta(
            {"summary": {"name": "Summary", "required": True}}
        )
        assert cmd.run(make_args()) == 0
        cmd.jira_client.create_issue.assert_called_once()
