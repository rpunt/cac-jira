"""
Module for handling the start of work on Jira issues.

This module provides functionality to transition Jira issues to an "In Progress" state,
indicating that work has begun on the issue. This allows teams to track which issues
are actively being worked on and by whom.
"""

# pylint: disable=broad-exception-caught

from cac_jira.commands.issue import JiraIssueCommand


class IssueBegin(JiraIssueCommand):
    """
    Command class for transitioning Jira issues to "In Progress".
    """

    def define_arguments(self, parser):
        """
        Define command-specific arguments.

        Args:
            parser: The argument parser to add arguments to
        """
        # Add common arguments first
        super().define_arguments(parser)
        parser.add_argument(
            "-i",
            "--issue",
            help="Issue to transition to In Progress",
            default=None,
            required=True,
        )
        return parser

    def execute(self, args):
        """
        Execute the command with the provided arguments.

        Args:
            args: The parsed arguments
        """
        self.log.debug("Transitioning Jira issue %s to In Progress", args.issue)
        issue = self.jira_client.issue(args.issue)
        if not issue:
            self.log.error("Issue not found")
            return
        self._transition_to(issue, "In Progress")
