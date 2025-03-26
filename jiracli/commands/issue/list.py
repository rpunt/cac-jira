#!/usr/bin/env python
# pylint: disable=line-too-long, no-member

"""
Fetches and prints a list of issues from the specified Jira project in a tabular format.
"""

from __future__ import annotations
from datetime import datetime
import cac_core as cac
from jiracli import JIRA_CLIENT

from . import IssueCommand

class IssueList(IssueCommand):
    """
    A command to list Jira issues for a specified project.

    This class provides functionality to define command-line arguments for filtering issues
    and to execute the command by fetching and displaying issues in a tabular format. It
    supports filtering issues assigned to the current user and excluding issues marked as "Done".
    """

    @classmethod
    def define_arguments(cls, parser):
        """
        Defines command-line arguments for filtering issues.
        """
        super().define_arguments(parser)
        parser.add_argument("-m", "--mine", action="store_true", help="List issues assigned to the current user")
        parser.add_argument("-d", "--done", action="store_true", help="Include issues that are done")

    def execute(self, args): #, **kwargs):
        """
        Fetches and prints a list of issues from the specified Jira project in a tabular format.

        This method constructs a JQL query based on the provided command-line arguments,
        fetches issues from Jira using pagination, processes the issues into models, and
        prints them in a tabular format.

        Args:
            args (argparse.Namespace): Parsed command-line arguments containing the following:
                - project (str): The Jira project key to filter issues (default: "CRDBOPS").
                - mine (bool): If True, filters issues assigned to the current user.
                - done (bool): If True, includes issues that are marked as "Done".

        Returns:
            None
        """
        log = cac.logger.new(__name__)
        log.debug("Executing 'jira issue listing' command...")

        jql_query = [f"project = {args.project}"]
        if args.mine:
            jql_query.append('assignee = currentUser()')
        if not args.done:
            jql_query.append('status != Done')
        jql_query_string = ' AND '.join(jql_query)

        start_at = 0
        max_results = 50  # Number of issues to fetch per request
        total_issues = []
        while True:
            issues = JIRA_CLIENT.search_issues(
                jql_query_string,
                startAt=start_at,
                maxResults=max_results,
                fields=[
                    "key",
                    "summary",
                    "status",
                    "assignee",
                    "issuetype",
                    "labels",
                    "resolutiondate",
                ],
            )

            total_issues.extend(issues)

            # Break the loop if we've fetched all issues
            if len(issues) < max_results:
                break

            # Update startAt for the next batch
            start_at += max_results

        models = []
        for issue in total_issues:
            assignee = issue.fields.assignee.displayName if issue.fields.assignee else 'Unassigned'
            resolution_date = datetime.strptime(issue.fields.resolutiondate, '%Y-%m-%dT%H:%M:%S.%f%z').strftime('%Y-%m-%d') if issue.fields.resolutiondate else 'N/A'

            model = cac.model.Model({
                'ID': issue.key,
                'Summary': issue.fields.summary,
                'Status': issue.fields.status.name,
                'Assignee': assignee,
                'Issue Type': issue.fields.issuetype.name,
                'Labels': ', '.join(issue.fields.labels),
                'Resolution Date': resolution_date
            })
            models.append(model)

        printer = cac.output.OutputTable({})
        printer.print_models(models)
