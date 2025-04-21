#!/usr/bin/env python
# pylint: disable=line-too-long, import-outside-toplevel, broad-exception-caught

"""
Command module for creating Jira issues.
"""

from cac_jira.commands.issue import JiraIssueCommand


class IssueClose(JiraIssueCommand):
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
        if not issue:
            self.log.error("Issue not found")
            return

        # Get all available transitions for the issue
        transitions = self.jira_client.transitions(issue)

        # Find the transition ID where name is "In Progress"
        closed_id = None
        desired_transition = "Done"
        for transition in transitions:
            if transition['name'] == desired_transition:
                closed_id = transition['id']
                self.log.debug("Found '%s' transition with ID: %s", desired_transition, closed_id)
                break

        if not closed_id:
            self.log.error("No '%s' transition found for this issue", desired_transition)
            # List all available transitions
            self.log.info("Available transitions:")
            for transition in transitions:
                self.log.info("  - %s (ID: %s)", transition['name'], transition['id'])
            return

        try:
            self.jira_client.transition_issue(issue, closed_id)
            self.log.info("Issue %s closed", issue.key)
        except Exception as e:
            self.log.error("Failed to transition issue: %s", str(e))
