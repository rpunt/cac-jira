#!/usr/bin/env python

"""
Base class for all Jira CLI commands.

This module provides a base class that all command actions should inherit from,
allowing for common functionality and arguments to be shared across different
command actions.
"""

import abc
from cac_core.command import Command
from cac_jira import JIRA_CLIENT, CONFIG, log


class JiraCommand(Command):
    """
    Base class for all Jira CLI commands.

    This class defines common methods and properties that should be shared
    across all command actions, such as common arguments, authentication,
    and utility functions.
    """

    def __init__(self):
        """
        Initialize the command with a logger and Jira client.
        """
        super().__init__()
        self.log = log
        self.jira_client = JIRA_CLIENT
        self.config = CONFIG

    # TODO: W0221 arguments differ
    def define_common_arguments(self, parser):
        """
        Define arguments common to all Jira commands.

        Args:
            parser: The argument parser to add arguments to
        """
        # Add the base common arguments
        super().define_common_arguments(parser)

        # Add Jira-specific common arguments
        return parser

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
        # Add common arguments first
        self.define_common_arguments(parser)
        return parser

    @abc.abstractmethod
    def execute(self, args):
        """
        Execute the command with the provided arguments.

        This method must be implemented by subclasses.

        Args:
            args: The parsed arguments
        """
        pass

    # TODO: this is unnecessary
    def format_output(self, data, output_format):
        """
        Format the data according to the specified output format.

        Args:
            data: The data to format
            output_format: The format to use (json, yaml, table, csv)

        Returns:
            Formatted data as a string
        """
        # Placeholder implementation
        self.log.debug("Formatting output as: %s", output_format)
        return f"Data formatted as {output_format}: {data}"
