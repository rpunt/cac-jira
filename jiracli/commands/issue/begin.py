#!/usr/bin/env python

from __future__ import annotations

# import tabulate
# from datetime import datetime
# import cac_core as cac

# from collections import Counter


class IssueBegin:
    def execute(self, *args, **kwargs):
        """
        https://jira.readthedocs.io/api.html#jira.client.JIRA.transition_issue
        client.transition_issue(args.issue, "In Progress")
        """
        print("Executing 'jira issue begin' command...")
