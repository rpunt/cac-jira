# pylint: disable=broad-except, line-too-long

"""
module docstring
"""

import sys
from importlib import metadata

import cac_core as cac

from cac_jira.core import client

try:
    __version__ = metadata.version(__package__)
except Exception:
    __version__ = "#N/A"

log = cac.logger.new(__name__)

CONFIG = None
JIRA_CLIENT = None
_initialized = False


def _initialize():
    global CONFIG, JIRA_CLIENT, _initialized  # pylint: disable=global-statement
    if _initialized:
        return

    cac.updatechecker.check_package_for_updates(__name__)
    log.debug("Initializing %s version %s", __name__, __version__)

    config = cac.config.Config(__name__)
    log.debug("user config path: %s", config.config_file)

    jira_server = config.get("server", "INVALID_DEFAULT").replace("https://", "")
    if jira_server == "INVALID_DEFAULT":
        jira_server = input("Enter your Jira server URL: ").strip().replace("https://", "")
        config.set("server", jira_server)
        config.server = jira_server
        config.save()

    jira_project = config.get("project", "INVALID_DEFAULT")
    if jira_project == "INVALID_DEFAULT":
        jira_project = input("Enter your default Jira project key (optional): ").strip()
        if jira_project:
            config.set("project", jira_project)
            config.project = jira_project
            config.save()

    credentialmanager = cac.credentialmanager.CredentialManager(__name__)
    auth_method = config.get("auth_method", "basic")

    if auth_method == "pat":
        jira_username = config.get("username", None)
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
        jira_username = config.get("username", "INVALID_DEFAULT")
        if jira_username == "INVALID_DEFAULT":
            jira_username = input("Enter your Jira username (email): ").strip()
            config.set("username", jira_username)
            config.username = jira_username
            config.save()
        jira_api_token = credentialmanager.get_credential(jira_username, "Jira API key")
        if not jira_api_token:
            log.error(
                "API token not found for %s; see https://github.com/rpunt/%s/blob/main/README.md#authentication",
                jira_username,
                __name__.replace("_", "-"),
            )
            sys.exit(1)

    CONFIG = config
    JIRA_CLIENT = client.JiraClient(jira_server, jira_username, jira_api_token, auth_method=auth_method)
    _initialized = True


__all__ = ["JIRA_CLIENT", "CONFIG", "log", "_initialize"]
