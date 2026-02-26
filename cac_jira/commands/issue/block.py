"""
Module for handling the blocking of Jira issues.

This module provides functionality to transition Jira issues to a "Blocked" state,
allowing users to mark issues that cannot proceed due to dependencies or other obstacles.
Users can optionally add a comment explaining why the issue is being blocked.
"""

# pylint: disable=broad-exception-caught

from cac_jira.commands.issue import JiraIssueCommand


class IssueBlock(JiraIssueCommand):
    """
    Command class for transitioning Jira issues to "Blocked".
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
            help="Issue to transition to Blocked",
            default=None,
            required=True,
        )
        parser.add_argument(
            "-c",
            "--comment",
            help="Comment to add when transitioning to Blocked",
            default=None,
            required=False,
        )
        return parser

    def execute(self, args):
        """
        Execute the command with the provided arguments.

        Args:
            args: The parsed arguments
        """
        self.log.debug("Transitioning Jira issue %s to Blocked", args.issue)
        issue = self.jira_client.issue(args.issue)
        if not issue:
            self.log.error("Issue not found")
            return
        self._transition_to(issue, "Blocked", comment=args.comment)
