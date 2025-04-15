#!/usr/bin/env python

"""
Base module for all project-related commands.

This module defines the base ProjectCommand class that all project-related
action classes should inherit from.
"""

from jiracli.commands.command import JiraCommand


class JiraProjectCommand(JiraCommand):
    """
    Base class for all project-related actions.

    This class defines common methods and properties that should be shared
    across all project actions, such as project-specific arguments and utilities.
    """

    def __init__(self):
        """
        Initialize the project command.
        """
        super().__init__()
        # Import here to avoid circular imports
        from jiracli import JIRA_CLIENT
        self.jira_client = JIRA_CLIENT

    def define_common_arguments(self, parser):
        """
        Define arguments common to all project actions.

        Args:
            parser: The argument parser to add arguments to
        """
        # Add base common arguments
        super().define_common_arguments(parser)

        # Add project-specific common arguments
        parser.add_argument(
            "--archived",
            help="Include archived projects",
            action="store_true",
            default=False
        )
        return parser

    def get_project_types(self):
        """
        Get available project types.

        Returns:
            List of project types
        """
        # This is a placeholder - in a real implementation, this would
        # fetch actual project types from the Jira API
        self.log.debug("Getting project types")
        return ["software", "business", "service_desk"]

    def get_project_templates(self):
        """
        Get available project templates.

        Returns:
            Dictionary of project templates
        """
        # Placeholder implementation
        self.log.debug("Getting project templates")
        return {
            "scrum": "Template for Scrum projects",
            "kanban": "Template for Kanban projects",
            "basic": "Basic project with no specific methodology"
        }
