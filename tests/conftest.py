"""
Pytest configuration for cac-jira tests.

Mocks are set up at module level so they take effect before test files
are collected and trigger cac_jira package imports.
"""

import os
from unittest.mock import MagicMock, patch

# Set config values via environment variables so cac_jira.__init__
# doesn't prompt for input. The Config class reads env vars prefixed
# with the uppercased module name.
os.environ.setdefault("CAC_JIRA_SERVER", "test.atlassian.net")
os.environ.setdefault("CAC_JIRA_USERNAME", "test@example.com")
os.environ.setdefault("CAC_JIRA_PROJECT", "TEST")

# Mock keyring so credential lookup returns a fake token
# instead of prompting via getpass
patch("keyring.get_password", return_value="fake-api-token").start()

# Mock the Jira client connection so tests don't need a real server
patch("jira.JIRA").start()

# Mock the update checker to avoid network calls
patch("cac_core.updatechecker.check_package_for_updates").start()
