#!/usr/bin/env python

from __future__ import annotations
# import tabulate
# from datetime import datetime
# import cac_core as cac

# from collections import Counter
class IssueAssign:
    def execute(self, *args, **kwargs):
        """
        https://jira.readthedocs.io/api.html#jira.client.JIRA.assign_issue
        client.assign_issue(args.issue, jira_username)
        """
        print("Executing 'jira issue assign' command...")
