#!/usr/bin/env python

"""
Base class for all Jira CLI commands.

This module provides a base class that all command actions should inherit from,
allowing for common functionality and arguments to be shared across different
command actions.
"""

import abc

from cac_core.command import Command
from jira.exceptions import JIRAError

import cac_jira
from cac_jira import log


class JiraCommand(Command):
    """
    Base class for all Jira CLI commands.

    This class defines common methods and properties that should be shared
    across all command actions, such as common arguments, authentication,
    and utility functions.
    """

    def __init__(self):
        """
        Initialize the command with a logger and configuration.

        Configuration is loaded eagerly (it is network-free and needed for
        argument defaults), but the Jira client is connected lazily on first
        access via the ``jira_client`` property so that argument parsing and
        ``--help`` do not require network access or credentials.
        """
        super().__init__()
        self.log = log
        self.config = cac_jira.CONFIG
        self._jira_client = None

    @property
    def jira_client(self):
        """The Jira client, connected on first access."""
        if self._jira_client is None:
            self._jira_client = cac_jira.JIRA_CLIENT
        return self._jira_client

    @jira_client.setter
    def jira_client(self, value):
        self._jira_client = value

    @abc.abstractmethod
    def define_arguments(self, parser):
        """
        Define command-specific arguments.

        This method must be implemented by subclasses to add
        command-specific arguments to the parser.

        Args:
            parser: The argument parser to add arguments to

        Returns:
            The updated argument parser
        """
        super().define_arguments(parser)
        return parser

    def execute(self, args):
        """
        Run the command and map failures to an exit code.

        This is a template method: it invokes the subclass's ``_execute()`` and
        turns any error raised by the Jira client into a logged, non-zero exit
        code. Centralizing the error handling here means individual commands do
        not need their own try/except around client calls -- they implement
        ``_execute()`` as straight-line logic and may raise freely (or return an
        explicit non-zero code for their own validation failures).

        Args:
            args: The parsed arguments

        Returns:
            int: The exit code (0 on success, non-zero on failure).
        """
        try:
            result = self._execute(args)
        except JIRAError as e:
            # python-jira raises this for not-found/auth/permission/JQL errors;
            # its ``text`` is the human-readable Jira message.
            self.log.error(
                "%s failed: %s", type(self).__name__, getattr(e, "text", None) or e
            )
            return 1
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.log.error("%s failed: %s", type(self).__name__, e)
            return 1
        return 0 if result is None else result

    @abc.abstractmethod
    def _execute(self, args):
        """
        Perform the command's work.

        Subclasses implement this as straight-line logic. Errors raised by the
        Jira client propagate to ``execute()``, which logs them and returns a
        non-zero exit code, so ``_execute()`` does not need to wrap client calls
        in try/except. Return ``None``/``0`` on success, or a non-zero int for
        command-specific validation failures.

        Args:
            args: The parsed arguments

        Returns:
            Optional[int]: ``None``/``0`` on success, non-zero on failure.
        """
        raise NotImplementedError("Command subclasses must implement _execute()")
