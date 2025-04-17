#!/usr/bin/env python

"""
Command module for creating Jira issues.
"""

from jiracli.commands.issue import JiraIssueCommand

class IssueCreate(JiraIssueCommand):
    """
    Command class for creating Jira issues.
    """

    def define_arguments(self, parser):
        """
        Define command-specific arguments.

        Args:
            parser: The argument parser to add arguments to
        """
        # Add common arguments first
        super().define_arguments(parser)

        # Add action-specific arguments
        parser.add_argument(
            "--summary",
            help="Issue summary",
            required=True
        )
        parser.add_argument(
            "--description",
            help="Issue description",
            default=""
        )
        parser.add_argument(
            "--type",
            help="Issue type (Bug, Task, Story, etc.)",
            default="Task"
        )
        # parser.add_argument(
        #     "--assignee",
        #     help="Assign the issue to a user",
        #     default=None
        # )
        return parser

    def execute(self, args):
        """
        Execute the command with the provided arguments.

        Args:
            args: The parsed arguments
        """
        # Validate project is provided (required for issue creation)
        if not args.project:
            self.log.error("Project key is required for issue creation")
            return 1

        # Prepare the issue data
        issue_data = {
            "project": args.project,
            "summary": args.summary,
            "description": args.description,
            "issuetype": args.type,
        }

        # if args.assignee:
        #     issue_data["assignee"] = args.assignee

        self.log.debug("Issue data: %s", issue_data)
        issue = self.jira_client.create_issue(
            fields=issue_data
        )
        self.log.info("Issue %s created successfully", issue.key)
