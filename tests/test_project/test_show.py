"""
Tests for the ProjectShow command.
"""

import argparse
from unittest.mock import MagicMock, patch

import pytest

from cac_jira.commands.project.show import ProjectShow


class TestProjectShow:
    """Test suite for the ProjectShow command."""

    @pytest.fixture
    def project_show_command(self):
        """Create a ProjectShow command instance."""
        with patch("cac_jira.JIRA_CLIENT"):
            command = ProjectShow()
            command.log = MagicMock()
            return command

    def test_define_arguments_requires_project(self, project_show_command):
        """The project key is a required positional argument."""
        parser = argparse.ArgumentParser()
        project_show_command.define_arguments(parser)

        args = parser.parse_args(["TEST"])
        assert args.project == "TEST"

        with pytest.raises(SystemExit):
            parser.parse_args([])

    @patch("cac_core.output.Output")
    def test_show_single_project(self, mock_output, project_show_command):
        """execute fetches exactly the requested project and renders one model."""
        mock_project = MagicMock()
        mock_project.id = "10001"
        mock_project.key = "TEST"
        mock_project.name = "Test Project"
        project_show_command.jira_client = MagicMock()
        project_show_command.jira_client.project.return_value = mock_project

        args = argparse.Namespace(project="TEST", output="table")
        result = project_show_command.run(args)

        assert result == 0
        project_show_command.jira_client.project.assert_called_once_with("TEST")
        models = mock_output.return_value.print_models.call_args[0][0]
        assert len(models) == 1
        assert models[0].Key == "TEST"
        assert models[0].Name == "Test Project"

    def test_show_project_not_found(self, project_show_command):
        """A lookup failure is reported and returns a non-zero exit code."""
        project_show_command.jira_client = MagicMock()
        project_show_command.jira_client.project.side_effect = Exception("Not found")

        args = argparse.Namespace(project="NOPE", output="table")
        result = project_show_command.run(args)

        assert result == 1
        project_show_command.log.error.assert_called()

    def test_show_project_none(self, project_show_command):
        """A falsy project is handled without an AttributeError."""
        project_show_command.jira_client = MagicMock()
        project_show_command.jira_client.project.return_value = None

        args = argparse.Namespace(project="NOPE", output="table")
        result = project_show_command.run(args)

        assert result == 1
        project_show_command.log.error.assert_called()
