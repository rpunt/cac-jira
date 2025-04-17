# #!/usr/bin/env python
# pylint: disable=no-member

from jiracli.commands.issue import JiraIssueCommand


class IssueDelete(JiraIssueCommand):
    """
    Command class for commenting on Jira issues.
    """

    def define_arguments(self, parser):
        """
        Define command-specific arguments.

        Args:
            parser: The argument parser to add arguments to
        """
        # Add common arguments first
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
        """
        Execute the command with the provided arguments.

        Args:
            args: The parsed arguments
        """
        self.log.debug("Deleting Jira issue")
        self.jira_client.issue(args.issue)
        self.log.info("Issue %s deleted", args.issue)
