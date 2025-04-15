#!/usr/bin/env python

"""
Command module for creating Jira issues.
"""

# import argparse
# import cac_core as cac
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
        parser.add_argument(
            "--assignee",
            help="Assign the issue to a user",
            default=None
        )
        parser.add_argument(
            "--priority",
            help="Issue priority",
            choices=["Highest", "High", "Medium", "Low", "Lowest"],
            default="Medium"
        )
        return parser

    def execute(self, args):
        """
        Execute the command with the provided arguments.

        Args:
            args: The parsed arguments
        """
        self.log.info("Creating Jira issue")

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
            "priority": args.priority
        }

        if args.assignee:
            issue_data["assignee"] = args.assignee

        self.log.debug("Issue data: %s", issue_data)

        # Use self.jira_client directly instead of get_jira_client()
        # Here you would make the actual API call to Jira
        # For demonstration purposes, we'll just print the data
        result = f"Would create Jira issue with data: {issue_data}"
        print(self.format_output(result, args.output))
