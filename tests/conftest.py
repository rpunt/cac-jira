"""
Pytest configuration for cac-jira tests.

Mocks are set up at module level so they take effect before cac_jira
initializes on first command instantiation.
"""

import os
from unittest.mock import patch

os.environ.setdefault("CAC_JIRA_SERVER", "test.atlassian.net")
os.environ.setdefault("CAC_JIRA_USERNAME", "test@example.com")
os.environ.setdefault("CAC_JIRA_PROJECT", "TEST")

patch("keyring.get_password", return_value="fake-api-token").start()
patch("jira.JIRA").start()
patch("cac_core.updatechecker.check_package_for_updates").start()
