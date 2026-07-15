#!/usr/bin/env python

"""
Command module for showing a single Jira project.
"""

import cac_core as cac

from cac_jira.commands.project import JiraProjectCommand


class ProjectShow(JiraProjectCommand):
    """
    Command class for showing details of a specific Jira project.
    """

    def define_arguments(self, parser):
        """
        Define command-specific arguments.

        Args:
            parser: The argument parser to add arguments to
        """
        super().define_arguments(parser)
        parser.add_argument(
            "project",
            help="Project key (or ID) to show",
        )
        return parser

    def _execute(self, args):
        """
        Execute the command with the provided arguments.

        Args:
            args: The parsed arguments
        """
        self.log.debug("Showing Jira project %s", args.project)

        project = self.jira_client.project(args.project)
        if not project:
            self.log.error("Project %s not found", args.project)
            return 1

        model = cac.model.Model(
            {"ID": project.id, "Key": project.key, "Name": project.name}
        )
        printer = cac.output.Output(args)
        printer.print_models([model])
        return 0
