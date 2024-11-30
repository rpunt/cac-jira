#!/usr/bin/env python

from __future__ import annotations
# import tabulate
from datetime import datetime
import cac_core as cac

# from collections import Counter

def list(client) -> None:
    """
    Fetches and prints a list of issues from the specified Jira project in a tabular format.

    Args:
        client (JIRA): An authenticated JIRA client instance.

    The function constructs a JQL query to fetch issues from the 'CRDBOPS' project
    that are not marked as 'Done'. It retrieves the key, summary, status, assignee,
    issue type, labels, and resolution date for each issue. The issues are then
    printed in a table format using the tabulate module.

    Note:
        - The function assumes that the 'jira' client is already authenticated.
        - The 'tabulate' module must be installed.
        - The 'datetime' module is used to format the resolution date.

    Example:
        jira_client = JIRA(server='https://your-jira-server', basic_auth=('email', 'api_token'))
        issue_list(jira_client)
    """
    project = 'CRDBOPS'

    jql_query = []
    jql_query.append(f"project = {project}")
    jql_query.append('status != Done') # unless opts[:done]
    # jql_query.append('assignee = currentUser()') # if opts[:mine]
    jql_query_string = ' AND '.join(jql_query)
    issues = client.search_issues(jql_query_string, fields = ['key','summary','status','assignee','issuetype','labels','resolutiondate'])


    # models = []
    # issues.each do |issue|
    #     assignee = issue.assignee.nil? ? 'unassigned' : issue.assignee.displayName
    #     completion_date = issue.resolutiondate.nil? ? 'N/A' : Date.parse(issue.resolutiondate).strftime('%Y-%m-%d')

    #     model = Cac::Core::Model.new(
    #         ID: issue.key,
    #         Type: issue.issuetype.name,
    #         Labels: issue.labels.join(', '),
    #         Summary: issue.summary,
    #         Status: issue.status.name,
    #         Completed: completion_date,
    #         Assignee: assignee
    #     )

    #     models << model
    # end
    # print_models models


    models = []
    for issue in issues:
        assignee = issue.fields.assignee.displayName if issue.fields.assignee else 'Unassigned'
        resolution_date = datetime.strptime(issue.fields.resolutiondate, '%Y-%m-%dT%H:%M:%S.%f%z').strftime('%Y-%m-%d') if issue.fields.resolutiondate else 'N/A'
        # models.append([
        #     issue.key,
        #     issue.fields.summary,
        #     issue.fields.status.name,
        #     issue.fields.assignee.displayName if issue.fields.assignee else 'Unassigned',
        #     issue.fields.issuetype.name,
        #     ', '.join(issue.fields.labels),
        #     resolution_date
        # ])

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
    # # Print the table
    # print(
    #     tabulate.tabulate(
    #         models,
    #         headers=['Key', 'Summary', 'Status', 'Assignee', 'Issue Type', 'Labels', 'Resolution Date'],
    #         tablefmt='fancy_grid'
    #     )
    # )
