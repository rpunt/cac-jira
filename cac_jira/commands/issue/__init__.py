#!/usr/bin/env python

"""
Base module for all issue-related commands.

This module defines the base JiraCommand class that all issue-related
action classes should inherit from.
"""

import abc

from cac_jira.commands.command import JiraCommand


class JiraIssueCommand(JiraCommand):
    """
    Base class for all issue-related actions.

    This class defines common methods and properties that should be shared
    across all issue actions, such as issue-specific arguments and utilities.
    """

    @abc.abstractmethod
    def define_arguments(self, parser):
        """
        Define arguments specific to this command.

        Args:
            parser: The argument parser to add arguments to

        Returns:
            The parser with arguments added
        """
        super().define_arguments(parser)
        # Add issue-specific common arguments
        has_project = any(action.dest == "project" for action in parser._actions)
        if not has_project:
            parser.add_argument(
                "--project",
                help="Project key for the issue",
                default=self.config.project,  # pylint: disable=no-member
            )
        return parser

    @abc.abstractmethod
    def execute(self, args):
        """
        Execute the command with the given arguments.

        Args:
            args: The parsed arguments

        Returns:
            The result of the command execution
        """
        raise NotImplementedError("Subclasses must implement execute()")

    def _transition_to(self, issue, transition_name, comment=None):
        """
        Transition an issue to the named state.

        Args:
            issue: The Jira issue object
            transition_name: The target transition name (case-insensitive)
            comment: Optional comment to add after transitioning

        Returns:
            True on success, False if the transition was not found or failed
        """
        transitions = self.jira_client.transitions(issue)

        transition_id = None
        matched_name = None
        for transition in transitions:
            if transition["name"].upper() == transition_name.upper():
                transition_id = transition["id"]
                matched_name = transition["name"]
                self.log.debug(
                    "Found '%s' transition with ID: %s", matched_name, transition_id
                )
                break

        if not transition_id:
            self.log.error("No '%s' transition found for this issue", transition_name)
            self.log.info("Available transitions:")
            for transition in transitions:
                self.log.info("  - %s (ID: %s)", transition["name"], transition["id"])
            return False

        try:
            self.jira_client.transition_issue(issue, transition_id)
            if comment:
                self.jira_client.add_comment(issue, comment)
                self.log.info('Added comment: "%s"', comment)
            self.log.info('Issue %s transitioned to "%s"', issue.key, matched_name)
            return True
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.log.error("Failed to transition issue: %s", str(e))
            return False

    # def get_issue_types(self, args) -> list:
    #     """
    #     Get available issue types for a project.

    #     Args:
    #         args: The parsed arguments containing project information

    #     Returns:
    #         List of issue types
    #     """
    #     # This is a placeholder - in a real implementation, this would
    #     # fetch actual issue types from the Jira API
    #     self.log.debug("Getting issue types for project: %s", args.project)
    #     # return ["Bug", "Task", "Story", "Epic"]
    #     issue_types = self.jira_client.issue_types() # pylint: disable=no-member
    #     if issue_types:
    #         self.log.debug("Issue types found: %s", issue_types)
    #         return issue_types
    #     self.log.error("No issue types found for project: %s", args.project)
    #     return []

    # def get_issue_fields(self, args) -> dict:
    #     """
    #     Get available fields for issue creation/editing.

    #     Args:
    #         args: The parsed arguments

    #     Returns:
    #         Dictionary of field metadata
    #     """
    #     # Placeholder implementation
    #     self.log.debug("Getting issue fields")
    #     # return {
    #     #     "summary": {"required": True, "type": "string"},
    #     #     "description": {"required": False, "type": "string"},
    #     #     "assignee": {"required": False, "type": "user"},
    #     #     "priority": {"required": False, "type": "option"},
    #     # }
    #     fields = self.jira_client.issue_fields() # pylint: disable=no-member
    #     if fields:
    #         self.log.debug("Issue fields found: %s", fields)
    #         return fields
    #     self.log.error("No issue fields found")
    #     return {}
