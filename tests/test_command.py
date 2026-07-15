"""
Tests for the JiraCommand.execute() template method, which centralizes the
mapping of command outcomes and client errors to process exit codes.
"""

from unittest.mock import MagicMock

from jira.exceptions import JIRAError

from cac_jira.commands.issue.show import IssueShow


def _cmd():
    # IssueShow is an arbitrary concrete command; we drive it via a stubbed
    # _execute to exercise the base class's execute() wrapper in isolation.
    command = IssueShow()
    command.log = MagicMock()
    return command


def test_success_return_passed_through():
    command = _cmd()
    command._execute = MagicMock(return_value=0)
    assert command.execute(object()) == 0


def test_none_return_treated_as_success():
    command = _cmd()
    command._execute = MagicMock(return_value=None)
    assert command.execute(object()) == 0


def test_nonzero_return_passed_through():
    command = _cmd()
    command._execute = MagicMock(return_value=2)
    assert command.execute(object()) == 2


def test_jira_error_mapped_to_nonzero():
    command = _cmd()
    command._execute = MagicMock(side_effect=JIRAError(status_code=404, text="nope"))
    assert command.execute(object()) == 1
    command.log.error.assert_called()


def test_unexpected_exception_mapped_to_nonzero():
    command = _cmd()
    command._execute = MagicMock(side_effect=RuntimeError("boom"))
    assert command.execute(object()) == 1
    command.log.error.assert_called()
