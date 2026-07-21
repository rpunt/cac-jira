"""
Tests for the IssueFields command (lists required/optional fields for a type).
"""

import argparse
from unittest.mock import MagicMock

import pytest

from cac_jira.commands.issue.fields import IssueFields


def make_args(project="TEST", issue_type=None):
    return argparse.Namespace(
        project=project, type=issue_type, output="table", verbose=False
    )


class TestIssueFields:
    @pytest.fixture
    def cmd(self):
        command = IssueFields()
        command.log = MagicMock()
        command.jira_client = MagicMock()
        return command

    def test_lists_issue_types_when_no_type(self, cmd, capsys):
        cmd.jira_client.createmeta.return_value = {
            "projects": [{"issuetypes": [{"name": "Bug"}, {"name": "Task"}]}]
        }

        assert cmd.run(make_args(issue_type=None)) == 0

        out = capsys.readouterr().out
        assert "Available issue types for TEST" in out
        assert "Bug" in out and "Task" in out

    def test_lists_required_and_optional_fields(self, cmd, capsys):
        cmd.jira_client.createmeta.return_value = {
            "projects": [
                {
                    "issuetypes": [
                        {
                            "name": "Bug",
                            "fields": {
                                "summary": {"name": "Summary", "required": True},
                                "priority": {
                                    "name": "Priority",
                                    "required": True,
                                    "allowedValues": [
                                        {"name": "High"},
                                        {"name": "Low"},
                                    ],
                                },
                                "labels": {"name": "Labels", "required": False},
                            },
                        }
                    ]
                }
            ]
        }

        assert cmd.run(make_args(issue_type="Bug")) == 0

        out = capsys.readouterr().out
        assert "Required fields for Bug in TEST" in out
        assert "Summary" in out
        assert "Options: High, Low" in out  # allowedValues rendered
        assert "Optional fields" in out
        assert "Labels" in out

    def test_type_matching_is_case_insensitive(self, cmd, capsys):
        cmd.jira_client.createmeta.return_value = {
            "projects": [{"issuetypes": [{"name": "Bug", "fields": {}}]}]
        }

        assert cmd.run(make_args(issue_type="bug")) == 0
        assert "Required fields for bug in TEST" in capsys.readouterr().out

    def test_type_not_found_exits_nonzero(self, cmd, capsys):
        # A not-found guard is a validation failure -> non-zero exit.
        cmd.jira_client.createmeta.return_value = {
            "projects": [{"issuetypes": [{"name": "Bug"}]}]
        }

        assert cmd.run(make_args(issue_type="Nonexistent")) == 1
        assert "not found in project TEST" in capsys.readouterr().out

    def test_metadata_error_exits_nonzero(self, cmd, capsys):
        # Malformed metadata (no projects) -> IndexError, reported as a failure.
        cmd.jira_client.createmeta.return_value = {"projects": []}

        assert cmd.run(make_args(issue_type="Bug")) == 1
        assert "Error retrieving field information" in capsys.readouterr().out
