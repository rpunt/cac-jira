#!/usr/bin/env python
# pylint: disable=line-too-long, import-outside-toplevel, broad-exception-caught

"""
Command module for creating Jira issues.
"""

import json
from jiracli.commands.issue import JiraIssueCommand


class IssueShow(JiraIssueCommand):
    """
    Command class for creating Jira issues.
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
        return parser

    def execute(self, args):
        issue = self.jira_client.issue(args.issue)
        print(json.dumps(issue.raw, indent=4))
