"""
Tests for the IssueList command.

This module tests the functionality of the IssueList command, including:
- Argument parsing
- Query building
- Output formatting
- Filter application
"""

import argparse
from unittest.mock import MagicMock, patch

import pytest

from cac_jira.commands.issue.list import IssueList


class TestIssueList:
    """Test suite for the IssueList command."""

    @pytest.fixture
    def issue_list_command(self):
        """Create an IssueList command instance."""
        with patch("cac_jira.JIRA_CLIENT") as mock_client:
            command = IssueList()
            command.log = MagicMock()
            return command

    @pytest.fixture
    def mock_issues(self):
        """Create mock issues for testing."""
        return [
            MagicMock(key="TEST-1", fields=MagicMock(summary="Test Issue 1")),
            MagicMock(key="TEST-2", fields=MagicMock(summary="Test Issue 2")),
            MagicMock(key="TEST-3", fields=MagicMock(summary="Test Issue 3")),
        ]

    def test_define_arguments(self, issue_list_command):
        """Test that arguments are correctly defined."""
        parser = argparse.ArgumentParser()
        parser = issue_list_command.define_arguments(parser)

        # Check for required arguments
        args = parser.parse_args(["--project", "TEST"])
        assert args.project == "TEST"

        # Check for optional arguments
        args = parser.parse_args(["--project", "TEST", "--mine"])
        assert args.mine is True
        assert args.done is False

        args = parser.parse_args(["--project", "TEST", "--done"])
        assert args.mine is False
        assert args.done is True

    @patch("cac_jira.JIRA_CLIENT")
    def test_jql_query_building(self, mock_client, issue_list_command):
        """Test that JQL queries are built correctly."""
        # Setup the mock to return a value
        mock_client.search_issues.return_value = []

        # Basic query
        args = argparse.Namespace(
            project="TEST", mine=False, done=False, output="table"
        )
        issue_list_command.execute(args)

        # Verify search_issues was called
        mock_client.search_issues.assert_called()

        # Extract the JQL - use safe access pattern
        call_args = mock_client.search_issues.call_args
        assert call_args is not None, "search_issues was not called"

        # Get the first positional argument (JQL)
        jql = call_args[0][0]
        assert "project = TEST" in jql
        assert "resolution = Unresolved" in jql

        # Reset the mock for the next test
        mock_client.search_issues.reset_mock()

        # Mine filter
        args = argparse.Namespace(project="TEST", mine=True, done=False, output="table")
        issue_list_command.execute(args)

        # Verify and safely extract JQL
        mock_client.search_issues.assert_called()
        call_args = mock_client.search_issues.call_args
        jql = call_args[0][0]
        assert "assignee = currentUser()" in jql

        # Reset again
        mock_client.search_issues.reset_mock()

        # Done filter
        args = argparse.Namespace(project="TEST", mine=False, done=True, output="table")
        issue_list_command.execute(args)

        # Verify and safely extract JQL
        mock_client.search_issues.assert_called()
        call_args = mock_client.search_issues.call_args
        jql = call_args[0][0]
        assert "resolution = Unresolved" not in jql

    @patch("cac_jira.JIRA_CLIENT")
    @patch("cac_core.output.Output")
    def test_output_formatting(
        self, mock_output, mock_client, issue_list_command, mock_issues
    ):
        """Test that output is formatted correctly."""
        mock_client.search_issues.return_value = mock_issues

        # Table output
        args = argparse.Namespace(
            project="TEST", mine=False, done=False, output="table"
        )
        issue_list_command.execute(args)

        # Verify Output class was initialized with correct format
        mock_output.assert_called_once()
        mock_output_instance = mock_output.return_value
        mock_output_instance.print_models.assert_called_once()

        # Check models passed to print_models
        models = mock_output_instance.print_models.call_args[0][0]
        assert len(models) == 3
        assert models[0].key == "TEST-1"
        assert models[1].key == "TEST-2"
        assert models[2].key == "TEST-3"
