"""
Tests for the IssueCreate command.

This module tests the functionality of the IssueCreate command, including:
- Argument parsing
- Issue creation
- Field validation
- Response handling
"""

import argparse
from unittest.mock import MagicMock, patch

import pytest

from cac_jira.commands.issue.create import IssueCreate


class TestIssueCreate:
    """Test suite for the IssueCreate command."""

    @pytest.fixture
    def issue_create_command(self):
        """Create an IssueCreate command instance."""
        with patch("cac_jira.JIRA_CLIENT"):
            command = IssueCreate()
            command.log = MagicMock()
            return command

    def test_define_arguments(self, issue_create_command):
        """Test that arguments are correctly defined."""
        parser = argparse.ArgumentParser()
        parser = issue_create_command.define_arguments(parser)

        # Check for required arguments
        args = parser.parse_args(
            [
                "--project",
                "TEST",
                "--title",
                "Test Issue",
                "--description",
                "Test description",
            ]
        )
        assert args.project == "TEST"
        assert args.title == "Test Issue"
        assert args.description == "Test description"

        # Check for optional arguments
        args = parser.parse_args(
            [
                "--project",
                "TEST",
                "--title",
                "Test Issue",
                "--description",
                "Test description",
                "--begin",
                "--browse",
            ]
        )
        assert args.begin is True
        assert args.browse is True

    @patch("cac_jira.JIRA_CLIENT")
    def test_issue_creation(self, mock_client, issue_create_command):
        """Test issue creation process."""
        # Mock the issue creation response
        mock_issue = MagicMock()
        mock_issue.key = "TEST-123"
        mock_client.create_issue.return_value = mock_issue

        args = argparse.Namespace(
            project="TEST",
            title="Test Issue",
            description="Test description",
            begin=False,
            browse=False,
            labels=None,
            epic=None,
            output="table",
        )

        result = issue_create_command.execute(args)

        # Verify client was called with correct parameters
        mock_client.create_issue.assert_called_once()
        call_kwargs = mock_client.create_issue.call_args[1]
        assert call_kwargs["project"] == "TEST"
        assert call_kwargs["summary"] == "Test Issue"
        assert call_kwargs["description"] == "Test description"

        # Verify result
        assert result.key == "TEST-123"

    @patch("cac_jira.JIRA_CLIENT")
    def test_issue_with_labels(self, mock_client, issue_create_command):
        """Test issue creation with labels."""
        mock_issue = MagicMock()
        mock_issue.key = "TEST-123"
        mock_client.create_issue.return_value = mock_issue

        args = argparse.Namespace(
            project="TEST",
            title="Test Issue",
            description="Test description",
            begin=False,
            browse=False,
            labels=["bug", "critical"],
            epic=None,
            output="table",
        )

        issue_create_command.execute(args)

        # Verify labels were included
        call_kwargs = mock_client.create_issue.call_args[1]
        assert "labels" in call_kwargs
        assert call_kwargs["labels"] == ["bug", "critical"]

    @patch("cac_jira.JIRA_CLIENT")
    def test_issue_with_epic(self, mock_client, issue_create_command):
        """Test issue creation with epic link."""
        mock_issue = MagicMock()
        mock_issue.key = "TEST-123"
        mock_client.create_issue.return_value = mock_issue

        args = argparse.Namespace(
            project="TEST",
            title="Test Issue",
            description="Test description",
            begin=False,
            browse=False,
            labels=None,
            epic="EPIC-456",
            output="table",
        )

        issue_create_command.execute(args)

        # Verify epic link was added
        mock_client.add_issues_to_epic.assert_called_once_with("EPIC-456", ["TEST-123"])
