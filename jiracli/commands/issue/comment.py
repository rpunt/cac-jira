#!/usr/bin/env python

from __future__ import annotations

# import tabulate
# from datetime import datetime
# import cac_core as cac

# from collections import Counter


class IssueComment:
    def execute(self, client) -> None:
        """
        https://jira.readthedocs.io/api.html#jira.client.JIRA.add_comment
        client.add_comment(args.issue, f"comment body")
        """
        print("Executing 'jira issue comment' command...")
