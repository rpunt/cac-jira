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

_initialized = False
_module_state = {}


def _initialize_config():
    """
    Load configuration and run first-run prompts.

    This is deliberately network-free: it only reads/writes the local config
    file and prompts on first run. It must remain cheap because it runs for
    every command during argument parsing (including ``--help``).
    """
    if "CONFIG" in _module_state:
        return

    log.debug("Initializing %s config version %s", __name__, __version__)

    config = cac.config.Config(__name__)
    log.debug("user config path: %s", config.config_file)

    jira_server = config.get("server", "INVALID_DEFAULT").replace("https://", "")
    if jira_server == "INVALID_DEFAULT":
        jira_server = (
            input("Enter your Jira server URL: ").strip().replace("https://", "")
        )
        config.set("server", jira_server)
        config.server = jira_server
        config.save()

    jira_username = config.get("username", "INVALID_DEFAULT")
    if jira_username == "INVALID_DEFAULT":
        jira_username = input("Enter your Jira username (email): ").strip()
        config.set("username", jira_username)
        config.username = jira_username
        config.save()

    jira_project = config.get("project", "INVALID_DEFAULT")
    if jira_project == "INVALID_DEFAULT":
        jira_project = input("Enter your default Jira project key (optional): ").strip()
        if jira_project:
            config.set("project", jira_project)
            config.project = jira_project
            config.save()

    _module_state["CONFIG"] = config


def _initialize_client():
    """
    Connect to the Jira server.

    Requires config and credentials and performs network I/O, so it is only
    invoked when a command actually needs the client (i.e. at execution time),
    not during argument parsing.
    """
    global _initialized  # pylint: disable=global-statement
    if "JIRA_CLIENT" in _module_state:
        return

    _initialize_config()
    config = _module_state["CONFIG"]

    cac.updatechecker.check_package_for_updates(__name__)

    jira_username = config.get("username", "INVALID_DEFAULT")
    jira_server = config.get("server", "INVALID_DEFAULT").replace("https://", "")

    credentialmanager = cac.credentialmanager.CredentialManager(__name__)
    jira_api_token = credentialmanager.get_credential(jira_username, "Jira API key")

    if not jira_api_token:
        log.error(
            "API token not found for %s; see https://github.com/rpunt/%s/blob/main/README.md#authentication",
            jira_username,
            __name__.replace("_", "-"),
        )
        sys.exit(1)

    try:
        _module_state["JIRA_CLIENT"] = client.JiraClient(
            jira_server, jira_username, jira_api_token
        )
    except client.JiraAuthenticationError as e:
        log.error("%s", e)
        sys.exit(1)
    _initialized = True


def _initialize():
    """Fully initialize the module (config + client).

    Retained for backwards compatibility; new code should rely on lazy
    attribute access (``cac_jira.CONFIG`` / ``cac_jira.JIRA_CLIENT``).
    """
    _initialize_client()


def __getattr__(name):
    """Lazy initialization when accessing module-level attributes.

    Accessing ``CONFIG`` only loads the local config; accessing ``JIRA_CLIENT``
    additionally connects to Jira. This keeps config-only consumers (e.g.
    argument defaults) from triggering a network connection.
    """
    if name == "CONFIG":
        _initialize_config()
        return _module_state["CONFIG"]
    if name == "JIRA_CLIENT":
        _initialize_client()
        return _module_state["JIRA_CLIENT"]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["JIRA_CLIENT", "CONFIG", "log", "_initialize"]
