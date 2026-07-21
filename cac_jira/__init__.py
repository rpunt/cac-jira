# pylint: disable=broad-except, line-too-long

"""
module docstring
"""

import sys
from importlib import metadata
from typing import TYPE_CHECKING, Callable, Optional, cast

import cac_core as cac
from cac_core.cli import make_main

from cac_jira.core import client

if TYPE_CHECKING:
    # These module-level attributes are provided lazily via ``__getattr__``;
    # declare their types so consumers (and ``__all__``) see them statically.
    from cac_core.config import Config

    CONFIG: Config
    JIRA_CLIENT: client.JiraClient

try:
    __version__ = metadata.version(__name__)
except Exception:
    __version__ = "#N/A"

log = cac.logger.new(__name__)

_initialized = False
_module_state: dict[str, object] = {}


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

    # First-run setup: prompt for any keys still at their sentinel. ensure_keys
    # skips prompting during shell completion (argcomplete sets ``_ARGCOMPLETE``
    # and hijacks stdio, so an interactive prompt would hang the shell); the
    # sentinel is left in place and every consumer treats it as "no value".
    #
    # ``username`` is only required for basic auth; PAT authenticates with the
    # token alone, so it is left out of the prompts when ``auth_method`` is
    # ``pat`` (the user opts in by setting that key in their config file).
    keys: list[tuple[str, str, bool, Optional[Callable[[str], str]]]] = [
        (
            "server",
            "Enter your Jira server URL: ",
            True,
            lambda v: v.replace("https://", ""),
        ),
    ]
    # Normalize so "PAT"/" pat " match the same branch as "pat".
    auth_method = (config.get("auth_method") or "basic").strip().lower()
    if auth_method != "pat":
        keys.append(("username", "Enter your Jira username (email): ", True, None))
    keys.append(
        (
            "project",
            "Enter your default Jira project key (optional): ",
            False,
            None,
        )
    )
    config.ensure_keys(keys)

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
    config = cast(cac.config.Config, _module_state["CONFIG"])

    cac.updatechecker.check_package_for_updates(__name__)

    jira_server = config.get("server", "INVALID_DEFAULT").replace("https://", "")
    # Normalize so "PAT"/" pat " match the same branch as "pat".
    auth_method = (config.get("auth_method") or "basic").strip().lower()

    credentialmanager = cac.credentialmanager.CredentialManager(__name__)

    if auth_method == "pat":
        # PAT (Bearer) auth: the token stands alone; username is optional and
        # the credential is stored under a fixed key rather than per-username.
        # An unconfigured username still holds the template sentinel, so treat
        # it as unset rather than leaking "INVALID_DEFAULT" into the client.
        jira_username = config.get("username", None)
        if jira_username == "INVALID_DEFAULT":
            jira_username = None
        jira_api_token = credentialmanager.get_credential(
            "_pat_token", "Jira Personal Access Token"
        )
        if not jira_api_token:
            log.error(
                "Personal Access Token not found; see https://github.com/rpunt/%s/blob/main/README.md#authentication",
                __name__.replace("_", "-"),
            )
            sys.exit(1)
    else:
        jira_username = config.get("username", "INVALID_DEFAULT")
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
            jira_server, jira_username, jira_api_token, auth_method=auth_method
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


# Console-script entry point (see [project.scripts] -> ``jira = cac_jira:main``).
# The framework owns discovery, argument parsing, completion, and dispatch; this
# module only supplies the package name, program name, and description.
main = make_main("cac_jira", "jira", "Jira CLI tool")


__all__ = ["JIRA_CLIENT", "CONFIG", "log", "main", "_initialize"]
