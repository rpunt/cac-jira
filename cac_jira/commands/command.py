#!/usr/bin/env python

"""
Base class for all Jira CLI commands.

This module provides a base class that all command actions should inherit from,
allowing for common functionality and arguments to be shared across different
command actions.
"""

import abc

from cac_core.command import Command

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

    @abc.abstractmethod
    def execute(self, args):
        """
        Execute the command with the provided arguments.

        This method must be implemented by subclasses.

        Contract: return an int exit code -- ``0`` on success and a non-zero
        value on failure. Subclasses should catch exceptions raised by the
        Jira client and log a command-specific error before returning non-zero,
        rather than letting them propagate to the top-level handler.

        Args:
            args: The parsed arguments

        Returns:
            int: The exit code (0 on success, non-zero on failure).
        """
        raise NotImplementedError("Command subclasses must implement execute()")
