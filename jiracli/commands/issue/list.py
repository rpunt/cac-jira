#!/usr/bin/env python
# pylint: disable=line-too-long

"""
Command module for listing Jira issues.
"""

# import argparse
from datetime import datetime
import cac_core as cac
from jiracli.commands.issue import JiraIssueCommand


class IssueList(JiraIssueCommand):
    """
    Command class for listing Jira issues.
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
        # parser.add_argument(
        #     "--assignee",
        #     help="Filter issues by assignee",
        #     default=None
        # )
        # parser.add_argument("--status", help="Filter issues by status", default=None)
        parser.add_argument("-m", "--mine", action="store_true", default=False, help="List issues assigned to the current user")
        parser.add_argument("-d", "--done", action="store_true", default=False, help="Include issues that are done")

        return parser

    def execute(self, args):
        """
        Execute the command with the provided arguments.

        Args:
            args: The parsed arguments
        """
        self.log.debug("Listing Jira issues")

        # Build JQL query based on provided filters
        jql_parts = [f"project = {args.project}"]
        # if args.assignee:
        #     jql_parts.append(f"assignee = {args.assignee}")
        # if args.status:
        #     jql_parts.append(f"status = '{args.status}'")
        if args.mine:
            jql_parts.append("assignee = currentUser()")
        if not args.done:
            jql_parts.append("status != Done")

        jql = " AND ".join(jql_parts) if jql_parts else ""
        self.log.debug("JQL query: %s", jql)

        # start_at = 0
        # max_results = 50  # Number of issues to fetch per request
        # total_issues = []
        # while True:
        #     issues = self.jira_client.search_issues( # pylint: disable=no-member
        #         jql,
        #         startAt=start_at,
        #         maxResults=max_results,
        #         fields=[
        #             "key",
        #             "summary",
        #             "status",
        #             "assignee",
        #             "issuetype",
        #             "labels",
        #             "resolutiondate",
        #         ],
        #     )

        #     total_issues.extend(issues)

        #     # Break the loop if we've fetched all issues
        #     if len(issues) < max_results:
        #         break

        #     # Update startAt for the next batch
        #     start_at += max_results
        total_issues = self.jira_client.search_issues(jql)

        models = []
        for issue in total_issues:
            assignee = issue.fields.assignee.displayName if issue.fields.assignee else 'Unassigned'
            resolution_date = datetime.strptime(issue.fields.resolutiondate, '%Y-%m-%dT%H:%M:%S.%f%z').strftime('%Y-%m-%d') if issue.fields.resolutiondate else 'N/A'

            model = cac.model.Model(
                {
                    "ID": issue.key,
                    "Summary": issue.fields.summary,
                    "Status": issue.fields.status.name,
                    "Assignee": assignee,
                    "Issue Type": issue.fields.issuetype.name,
                    "Labels": ", ".join(issue.fields.labels),
                    "Resolution Date": resolution_date,
                }
            )
            models.append(model)

        printer = cac.output.Output({"json": args.json})
        printer.print_models(models)
