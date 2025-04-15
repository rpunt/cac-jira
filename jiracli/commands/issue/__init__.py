#!/usr/bin/env python

"""
Base module for all issue-related commands.

This module defines the base JiraCommand class that all issue-related
action classes should inherit from.
"""

import cac_core as cac
from jiracli.commands.command import JiraCommand


class JiraIssueCommand(JiraCommand):
    """
    Base class for all issue-related actions.

    This class defines common methods and properties that should be shared
    across all issue actions, such as issue-specific arguments and utilities.
    """

    def __init__(self):
        """
        Initialize the command with issue-specific settings.
        """
        super().__init__()
        # Using the logger already initialized in the parent class (JiraCommand)

    def define_common_arguments(self, parser):
        """
        Define arguments common to all issue actions.

        Args:
            parser: The argument parser to add arguments to
        """
        # Add base common arguments
        super().define_common_arguments(parser)

        # Add issue-specific common arguments
        parser.add_argument(
            "--project",
            help="Project key for the issue",
            default="CRDBOPS"
        )
        return parser

    def get_issue_types(self, args):
        """
        Get available issue types for a project.

        Args:
            args: The parsed arguments containing project information

        Returns:
            List of issue types
        """
        # This is a placeholder - in a real implementation, this would
        # fetch actual issue types from the Jira API
        self.log.debug("Getting issue types for project: %s", args.project)
        return ["Bug", "Task", "Story", "Epic"]

    def get_issue_fields(self, args):
        """
        Get available fields for issue creation/editing.

        Args:
            args: The parsed arguments

        Returns:
            Dictionary of field metadata
        """
        # Placeholder implementation
        self.log.debug("Getting issue fields")
        return {
            "summary": {"required": True, "type": "string"},
            "description": {"required": False, "type": "string"},
            "assignee": {"required": False, "type": "user"},
            "priority": {"required": False, "type": "option"},
        }
