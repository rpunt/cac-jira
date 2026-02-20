"""
Tests for the IssueDelete command.

This module tests the functionality of the IssueDelete command, including:
- Argument parsing
- Issue deletion
- Confirmation handling
"""

import argparse
from unittest.mock import MagicMock, patch

import pytest

from cac_jira.commands.issue.delete import IssueDelete


class TestIssueDelete:
    """Test suite for the IssueDelete command."""

    @pytest.fixture
    def issue_delete_command(self):
        """Create an IssueDelete command instance."""
        with patch("cac_jira.JIRA_CLIENT"):
            command = IssueDelete()
            command.log = MagicMock()
            return command

    def test_define_arguments(self, issue_delete_command):
        """Test that arguments are correctly defined."""
        parser = argparse.ArgumentParser()
        parser = issue_delete_command.define_arguments(parser)

        # Check for required arguments
        args = parser.parse_args(["--issue", "TEST-123"])
        assert args.issue == "TEST-123"

        # Check for optional arguments
        args = parser.parse_args(["--issue", "TEST-123", "--force"])
        assert args.issue == "TEST-123"
        assert args.force is True

    @patch("cac_jira.JIRA_CLIENT")
    @patch("builtins.input", return_value="y")
    def test_delete_with_confirmation(
        self, mock_input, mock_client, issue_delete_command
    ):
        """Test issue deletion with user confirmation."""
        args = argparse.Namespace(issue="TEST-123", force=False, output="table")

        issue_delete_command.execute(args)

        # Verify confirmation was requested
        mock_input.assert_called_once()
        # Verify issue was deleted
        mock_client.delete_issue.assert_called_once_with("TEST-123")

    @patch("cac_jira.JIRA_CLIENT")
    @patch("builtins.input", return_value="n")
    def test_delete_cancelled(self, mock_input, mock_client, issue_delete_command):
        """Test cancellation of issue deletion."""
        args = argparse.Namespace(issue="TEST-123", force=False, output="table")

        issue_delete_command.execute(args)

        # Verify confirmation was requested
        mock_input.assert_called_once()
        # Verify issue was not deleted
        mock_client.delete_issue.assert_not_called()
        # Verify cancellation was logged
        issue_delete_command.log.info.assert_called_with("Delete operation cancelled.")

    @patch("cac_jira.JIRA_CLIENT")
    @patch("builtins.input")
    def test_delete_with_force(self, mock_input, mock_client, issue_delete_command):
        """Test issue deletion with force flag."""
        args = argparse.Namespace(issue="TEST-123", force=True, output="table")

        issue_delete_command.execute(args)

        # Verify confirmation was not requested
        mock_input.assert_not_called()
        # Verify issue was deleted
        mock_client.delete_issue.assert_called_once_with("TEST-123")
