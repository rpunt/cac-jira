# pylint: disable=broad-except, line-too-long

"""
module docstring
"""

# import os
import sys
from importlib import metadata
import cac_core as cac
# import yaml
# import keyring
import cac_jira.core.client as client

if sys.version_info < (3, 9):
    print("This project requires Python 3.9 or higher.", file=sys.stderr)
    sys.exit(1)

cac.updatechecker.check_package_for_updates(__name__)

try:
    __version__ = metadata.version(__package__)
except Exception:
    __version__ = "#N/A"

log = cac.logger.new(__name__)
log.debug("Initializing %s version %s", __name__, __version__)

CONFIG = cac.config.Config(__name__)

log.debug("user config path: %s", CONFIG.config_file)

auth_method = CONFIG.get("auth_method", "basic")

jira_server = CONFIG.get("server", "INVALID_DEFAULT").replace("https://", "")
if jira_server == "INVALID_DEFAULT":
    jira_server = input("Enter your Jira server URL: ").strip().replace("https://", "")
    CONFIG.set("server", jira_server)
    CONFIG.server = jira_server
    CONFIG.save()

jira_project = CONFIG.get('project', 'INVALID_DEFAULT')
if jira_project == "INVALID_DEFAULT":
    jira_project = input("Enter your default Jira project key (optional): ").strip()
    if jira_project:
        CONFIG.set("project", jira_project)
        CONFIG.project = jira_project
        CONFIG.save()

credentialmanager = cac.credentialmanager.CredentialManager(__name__)

if auth_method == "pat":
    jira_username = CONFIG.get('username', None)
    jira_api_token = credentialmanager.get_credential(
        "_pat_token",
        "Jira Personal Access Token",
    )
    if not jira_api_token:
        log.error(
            "Personal Access Token not found; see https://github.com/rpunt/%s/blob/main/README.md#authentication",
            __name__.replace("_", "-"),
        )
        sys.exit(1)
else:
    jira_username = CONFIG.get('username', 'INVALID_DEFAULT')
    if jira_username == "INVALID_DEFAULT":
        jira_username = input("Enter your Jira username (email): ").strip()
        CONFIG.set("username", jira_username)
        CONFIG.username = jira_username
        CONFIG.save()
    jira_api_token = credentialmanager.get_credential(
        jira_username,
        "Jira API key",
    )
    if not jira_api_token:
        log.error(
            "API token not found for %s; see https://github.com/rpunt/%s/blob/main/README.md#authentication",
            jira_username,
            __name__.replace("_", "-"),
        )
        sys.exit(1)

JIRA_CLIENT = client.JiraClient(jira_server, jira_username, jira_api_token, auth_method=auth_method)

__all__ = ["JIRA_CLIENT", "CONFIG", "log"]
