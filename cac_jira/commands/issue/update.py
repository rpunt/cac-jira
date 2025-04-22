# #!/usr/bin/env python
# pylint: disable=no-member

from cac_jira.commands.issue import JiraIssueCommand


class IssueUpdate(JiraIssueCommand):
    """
    Command class for updating the title or description on Jira issues.
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
        parser.add_argument(
            "-t",
            "--title",
            help="New issue title",
            default=None,
        )
        parser.add_argument(
            "-d",
            "--description",
            help="New issue description",
            default=None,
        )
        return parser

    def execute(self, args):
        """
        Execute the command with the provided arguments.

        Args:
            args: The parsed arguments
        """
        self.log.debug("Updating Jira issue %s", args.issue)

        # Assign the issue to the user
        issue = self.jira_client.issue(args.issue)
        if not issue:
            self.log.error("Issue not found")
            return
        if args.title and args.description:
            issue.update(summary=args.title, description=args.description)
            self.log.info("Issue %s updated with new title and description", issue.key)
        elif args.title:
            issue.update(summary=args.title)
            self.log.info("Issue %s updated with new title", issue.key)
        elif args.description:
            issue.update(description=args.description)
            self.log.info("Issue %s updated with new description", issue.key)
