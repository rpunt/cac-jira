# pylint: disable=import-outside-toplevel
"""

Base module for all project-related commands.

This module defines the base ProjectCommand class that all project-related
action classes should inherit from.
"""

import abc

from cac_jira.commands.command import JiraCommand


class JiraProjectCommand(JiraCommand):
    """
    Base class for all project-related actions.

    This class defines common methods and properties that should be shared
    across all project actions, such as project-specific arguments and utilities.
    """

    @abc.abstractmethod
    def define_arguments(self, parser):
        """
        Define arguments specific to this command.

        Args:
            parser: The argument parser to add arguments to

        Returns:
            The modified parser
        """
        super().define_arguments(parser)
        # Note: filtering options (--name/--key) are specific to listing and are
        # defined by ProjectList, not here, so commands like `project show` don't
        # advertise filters that have no effect.
        return parser

    @abc.abstractmethod
    def execute(self, args):
        """
        Perform the command's work (see JiraCommand.execute).

        Args:
            args: The parsed command line arguments

        Returns:
            Optional[int]: None/0 on success, non-zero on failure.
        """
        # This method is meant to be overridden by specific project commands
        raise NotImplementedError("Subclasses must implement execute()")

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
            "basic": "Basic project with no specific methodology",
        }
