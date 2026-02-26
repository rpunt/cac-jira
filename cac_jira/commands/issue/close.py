"""
Module for handling the closure of Jira issues.

This module provides functionality to transition Jira issues to a "Done" state,
marking them as complete. Users can optionally add a closing comment to provide
context about the resolution of the issue.
"""

# pylint: disable=broad-exception-caught

from cac_jira.commands.issue import JiraIssueCommand


class IssueClose(JiraIssueCommand):
    """
    Command class for transitioning Jira issues to "Done".
    """

    def define_arguments(self, parser):
        """
        Define command-specific arguments.

        Args:
            parser: The argument parser to add arguments to
        """
        super().define_arguments(parser)
        parser.add_argument(
            "-i",
            "--issue",
            help="Issue to match",
            default=None,
            required=True,
        )
        parser.add_argument(
            "-c",
            "--comment",
            help="Comment to add when transitioning to Done",
            default=None,
            required=False,
        )
        return parser

    def execute(self, args):
        self.log.debug("Closing Jira issue %s", args.issue)
        issue = self.jira_client.issue(args.issue)
        if not issue:
            self.log.error("Issue not found")
            return
        self._transition_to(issue, "Done", comment=args.comment)
