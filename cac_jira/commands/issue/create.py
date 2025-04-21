#!/usr/bin/env python
# pylint: disable=line-too-long, import-outside-toplevel, broad-exception-caught

"""
Command module for creating Jira issues.
"""

import webbrowser
from cac_jira.commands.issue import JiraIssueCommand

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
            "-t",
            "--title",
            help="Issue title",
            required=True
        )
        parser.add_argument(
            "-d",
            "--description",
            help="Issue description",
            required=True
        )

        # TODO: get list of valid types from Jira
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

        parser.add_argument(
            "--assign",
            help="'Assign the issue to yourself?",
            action="store_true",
            default=False
        )

        parser.add_argument(
            "--begin",
            help="Mark issue in-progress",
            action="store_true",
            default=False
        )

        parser.add_argument(
            "--epic",
            help="Tie this issue to an existing Epic",
            default=None
        )

        parser.add_argument(
            "--labels",
            help="A comma-separated list of labels to apply to the issue",
            default=None
        )

        parser.add_argument(
            "--epic_name", help="Name your Epic", default=None
        )

        parser.add_argument(
            "--browse", help="Open the issue in your browser once created", action="store_true", default=False
        )

        return parser

    def execute(self, args):
        """
        Execute the command with the provided arguments.

        Args:
            args: The parsed arguments
        """
        if args.begin:
            args.assign = True
        # Validate project is provided (required for issue creation)
        if not args.project:
            self.log.error("Project key is required for issue creation")
            return 1

        # validate project
        try:
            project = self.jira_client.project(args.project)
            self.log.debug("Project %s found", project.key)
        except Exception as e:
            self.log.error("Failed to find project %s: %s", args.project, e)
            return 1

        # validate issue type
        try:
            project = self.jira_client.project(args.project)
            # Get all issue types for the project
            issuetypes = project.issueTypes

            # Find the matching issue type
            matching_issuetype = None
            valid_types = []
            for issuetype in issuetypes:
                valid_types.append(issuetype.name)
                if issuetype.name.lower() == args.type.lower():
                    matching_issuetype = {"name": issuetype.name}
                    break

            if matching_issuetype is None:
                raise ValueError(f"Invalid issue type '{args.type}' for project '{args.project}'\nValid issue types are: {', '.join(valid_types)}")

        except Exception as e:
            print(f"Error: {e}")
            return

        # Prepare the issue data
        fieldset = {
            "project": args.project,
            "summary": args.title,
            "description": args.description,
            "issuetype": matching_issuetype,
        }

        if args.labels:
            self.log.debug("Adding labels: %s", args.labels)
            fieldset['labels'] = args.labels.split(',')

        if args.epic:
            epic = self.jira_client.issue(args.epic).key
            self.log.debug("Adding to epic: %s", epic)
            fieldset["parent"] = {"key": epic}

        # if args.assignee:
        #     issue_data["assignee"] = args.assignee

        # TODO: handle epic creation
        # # If creating an epic, an epic name is required
        # if args.type == 'Epic':
        #     if args.epic_name is None:
        #         self.log.error("Epic Name is required if creating an Epic")
        #         return 1
        #     else:
        #         epic_name_field = self.jira_client.Field.all().select(lambda f: f.name == 'Epic Name').first().id
        #         fieldset[epic_name_field] = args.epic_name

        self.log.debug("Issue data: %s", fieldset)
        issue = self.jira_client.create_issue(fields=fieldset)
        self.log.info("Issue %s created successfully", issue.key)

        if args.assign:
            issue.update(assignee={"accountId": self.jira_client.current_user()})
            self.log.info("Issue %s assigned to you", issue.key)

        if args.begin:
            try:
                # Import the begin command module
                from cac_jira.commands.issue.begin import IssueBegin

                # Create a begin command instance
                begin_cmd = IssueBegin()

                # Prepare args for the begin command
                # We need to simulate args with an 'issue' attribute containing the new issue key
                from argparse import Namespace
                begin_args = Namespace(issue=issue.key)

                # Execute the begin command with our constructed args
                begin_cmd.execute(begin_args)
            except Exception as e:
                self.log.error("Failed to transition issue to In Progress: %s", str(e))

        if args.browse:
            webbrowser.open(issue.permalink())
