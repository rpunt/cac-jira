"""
Tests for exit-code propagation in the CLI entry point.
"""

import sys
from unittest.mock import patch

import pytest

from cac_jira.cli.main import main
from cac_jira.commands.issue.show import IssueShow


class TestMainExitCodes:
    """main() must surface failures as non-zero exit codes."""

    def test_nonzero_return_causes_exit(self, monkeypatch):
        """A truthy return value from execute() becomes the process exit code."""
        monkeypatch.setattr(sys, "argv", ["jira", "issue", "show", "-i", "TEST-1"])
        with patch.object(IssueShow, "execute", return_value=1):
            with pytest.raises(SystemExit) as exc:
                main()
        assert exc.value.code == 1

    def test_exception_causes_exit(self, monkeypatch):
        """An exception raised by execute() results in a non-zero exit."""
        monkeypatch.setattr(sys, "argv", ["jira", "issue", "show", "-i", "TEST-1"])
        with patch.object(IssueShow, "execute", side_effect=RuntimeError("boom")):
            with pytest.raises(SystemExit) as exc:
                main()
        assert exc.value.code == 1

    def test_success_does_not_exit(self, monkeypatch):
        """A None/0 return means success and must not raise SystemExit."""
        monkeypatch.setattr(sys, "argv", ["jira", "issue", "show", "-i", "TEST-1"])
        with patch.object(IssueShow, "execute", return_value=None):
            # Should complete without raising.
            main()
