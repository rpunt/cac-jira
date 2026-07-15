# #!/usr/bin/env python
# pylint: disable=broad-exception-caught

from cac_jira.commands.issue import JiraIssueCommand


class IssueDelete(JiraIssueCommand):
    """
    Command class for deleting Jira issues.
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
            "-f",
            "--force",
            help="Delete without confirmation",
            action="store_true",
            default=False,
        )
        return parser

    def _execute(self, args):
        """
        Execute the command with the provided arguments.

        Args:
            args: The parsed arguments
        """
        self.log.debug("Deleting Jira issue %s", args.issue)

        # Deletion is irreversible, so confirm unless --force was given.
        if not args.force:
            try:
                response = input(
                    f"Delete issue {args.issue}? This cannot be undone [y/N]: "
                )
            except EOFError:
                # No interactive stdin (piped input, CI, etc.).
                self.log.error(
                    "Cannot confirm deletion without an interactive terminal; "
                    "pass --force to delete non-interactively"
                )
                return 1
            if response.strip().lower() not in ("y", "yes"):
                self.log.info("Delete operation cancelled.")
                return 0

        self.jira_client.delete_issue(args.issue)
        self.log.info("Issue %s deleted", args.issue)
        return 0
