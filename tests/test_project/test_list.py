"""
Tests for the ProjectList command.
"""

import argparse
from unittest.mock import MagicMock, patch

import pytest

from cac_jira.commands.project.list import ProjectList


def make_project(pid, key, name):
    project = MagicMock()
    project.id = pid
    project.key = key
    project.name = name
    return project


class TestProjectList:
    @pytest.fixture
    def cmd(self):
        command = ProjectList()
        command.log = MagicMock()
        command.jira_client = MagicMock()
        return command

    @patch("cac_core.output.Output")
    def test_list_all(self, mock_output, cmd):
        cmd.jira_client.projects.return_value = [
            make_project("1", "AAA", "Alpha"),
            make_project("2", "BBB", "Beta"),
        ]

        result = cmd.execute(argparse.Namespace(name=None, key=None, output="table"))

        assert result == 0
        models = mock_output.return_value.print_models.call_args[0][0]
        assert len(models) == 2

    @patch("cac_core.output.Output")
    def test_filter_by_name(self, mock_output, cmd):
        cmd.jira_client.projects.return_value = [
            make_project("1", "AAA", "Alpha"),
            make_project("2", "BBB", "Beta"),
        ]

        result = cmd.execute(argparse.Namespace(name="alph", key=None, output="table"))

        assert result == 0
        models = mock_output.return_value.print_models.call_args[0][0]
        assert len(models) == 1
        assert models[0].Key == "AAA"

    def test_no_projects_returns_error(self, cmd):
        cmd.jira_client.projects.return_value = []

        result = cmd.execute(argparse.Namespace(name=None, key=None, output="table"))

        assert result == 1
        cmd.log.error.assert_called()
