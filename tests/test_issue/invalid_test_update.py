"""
Tests for the IssueUpdate command.

This module tests the functionality of the IssueUpdate command, including:
- Argument parsing
- Field validation
- Update operations
"""

import argparse
import pytest
from unittest.mock import MagicMock, patch

from cac_jira.commands.issue.update import IssueUpdate


class TestIssueUpdate:
    """Test suite for the IssueUpdate command."""

    @pytest.fixture
    def issue_update_command(self):
        """Create an IssueUpdate command instance."""
        with patch("cac_jira.JIRA_CLIENT"):
            command = IssueUpdate()
            command.log = MagicMock()
            return command

    @pytest.fixture
    def mock_issue(self):
        """Create a mock issue for testing."""
        issue = MagicMock()
        issue.key = "TEST-123"
        issue.fields.summary = "Original Title"
        issue.fields.description = "Original Description"
        return issue

    def test_define_arguments(self, issue_update_command):
        """Test that arguments are correctly defined."""
        parser = argparse.ArgumentParser()
        parser = issue_update_command.define_arguments(parser)

        # Check for required arguments
        args = parser.parse_args(["--issue", "TEST-123"])
        assert args.issue == "TEST-123"

        # Check with title update
        args = parser.parse_args(["--issue", "TEST-123", "--title", "New Title"])
        assert args.issue == "TEST-123"
        assert args.title == "New Title"

        # Check with description update
        args = parser.parse_args(
            ["--issue", "TEST-123", "--description", "New Description"]
        )
        assert args.issue == "TEST-123"
        assert args.description == "New Description"

        # Check with both updates
        args = parser.parse_args(
            [
                "--issue",
                "TEST-123",
                "--title",
                "New Title",
                "--description",
                "New Description",
            ]
        )
        assert args.issue == "TEST-123"
        assert args.title == "New Title"
        assert args.description == "New Description"

    @patch("cac_jira.JIRA_CLIENT")
    def test_update_title_only(self, mock_client, issue_update_command, mock_issue):
        """Test updating only the title/summary."""
        mock_client.issue.return_value = mock_issue

        args = argparse.Namespace(
            issue="TEST-123", title="New Title", description=None, output="table"
        )

        issue_update_command.execute(args)

        # Verify issue was updated with correct fields
        mock_issue.update.assert_called_once()
        call_kwargs = mock_issue.update.call_args[1]
        assert "summary" in call_kwargs
        assert call_kwargs["summary"] == "New Title"
        assert "description" not in call_kwargs

    @patch("cac_jira.JIRA_CLIENT")
    def test_update_description_only(
        self, mock_client, issue_update_command, mock_issue
    ):
        """Test updating only the description."""
        mock_client.issue.return_value = mock_issue

        args = argparse.Namespace(
            issue="TEST-123", title=None, description="New Description", output="table"
        )

        issue_update_command.execute(args)

        # Verify issue was updated with correct fields
        mock_issue.update.assert_called_once()
        call_kwargs = mock_issue.update.call_args[1]
        assert "description" in call_kwargs
        assert call_kwargs["description"] == "New Description"
        assert "summary" not in call_kwargs

    @patch("cac_jira.JIRA_CLIENT")
    def test_update_both_fields(self, mock_client, issue_update_command, mock_issue):
        """Test updating both title and description."""
        mock_client.issue.return_value = mock_issue

        args = argparse.Namespace(
            issue="TEST-123",
            title="New Title",
            description="New Description",
            output="table",
        )

        issue_update_command.execute(args)

        # Verify issue was updated with correct fields
        mock_issue.update.assert_called_once()
        call_kwargs = mock_issue.update.call_args[1]
        assert "summary" in call_kwargs
        assert call_kwargs["summary"] == "New Title"
        assert "description" in call_kwargs
        assert call_kwargs["description"] == "New Description"

    @patch("cac_jira.JIRA_CLIENT")
    def test_update_no_fields(self, mock_client, issue_update_command):
        """Test execution with no fields to update."""
        args = argparse.Namespace(
            issue="TEST-123", title=None, description=None, output="table"
        )

        issue_update_command.execute(args)

        # Verify issue was not updated
        mock_client.issue.return_value.update.assert_not_called()
        # Verify warning was logged
        issue_update_command.log.warning.assert_called_once()
