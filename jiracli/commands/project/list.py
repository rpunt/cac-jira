#!/usr/bin/env python

"""
Command module for listing Jira projects.
"""

from jiracli.commands.project import JiraProjectCommand

class ProjectList(JiraProjectCommand):
    """
    Command class for listing Jira projects.
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
            "--type",
            help="Filter by project type",
            choices=["software", "business"],
            default=None
        )
        return parser

    def execute(self, args):
        """
        Execute the command with the provided arguments.

        Args:
            args: The parsed arguments
        """
        self.log.info("Listing Jira projects")

        # Build the query parameters
        params = {}
        if args.type:
            params["projectTypeKey"] = args.type
        if not args.archived:
            params["expand"] = "description,lead"

        self.log.debug("Query parameters: %s", params)

        # Use self.jira_client directly instead of get_jira_client()
        # Here you would make the actual API call to Jira
        # For demonstration purposes, we'll just print the parameters
        result = f"Would query Jira projects with params: {params}"
        print(self.format_output(result, args.output))
