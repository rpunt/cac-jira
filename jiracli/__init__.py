# pylint: disable=broad-except, line-too-long

"""
module docstring
"""

import os
import sys
from importlib import metadata
import cac_core as cac
import yaml
import keyring
import jiracli.core.client as client

if sys.version_info < (3, 8):
    print("This project requires Python 3.8 or higher.", file=sys.stderr)
    sys.exit(1)

try:
    __version__ = metadata.version(__package__)
except Exception:
    __version__ = "#N/A"

log = cac.logger.new(__name__)
log.debug("Initializing %s version %s", __name__, __version__)

CONFIG = cac.config.Config(__name__)
default_config = {}
default_config_dir = os.path.join(os.path.dirname(__file__), 'config')
default_config_file = os.path.join(default_config_dir, f"{__name__}.yaml")
if os.path.exists(default_config_file):
    with open(default_config_file, 'r', encoding='utf-8') as f:
        default_config.update(yaml.safe_load(f))
config = CONFIG.load(__name__, default_config)

log.debug("user config path: %s", config['config_file_path'])

# TODO: prompt user for server and username if not set
server = config.get('server', 'INVALID_DEFAULT').replace('https://', '')
if config['server'] == 'INVALID_DEFAULT':
    log.error("Invalid server in %s: %s", config['config_file_path'], server)
    sys.exit(1)

username = CONFIG.get('username', 'INVALID_DEFAULT')
if username == 'INVALID_DEFAULT':
    log.error("Invalid username in %s: %s", CONFIG.config_file, username)
    sys.exit(1)

def read_keychain_password(username):
    """
    Get the Jira API token from the system keychain.
    If not found, prompt user to enter it.

    Args:
        username: The username to get the API token for

    Returns:
        The API token as a string
    """
    # Check if API token exists in keychain
    keychain_item_password = keyring.get_password(__name__, username)

    # If API token not found, prompt user to enter it
    if not keychain_item_password:
        import getpass # pylint: disable=import-outside-toplevel
        log.info(
            "API token not found for %s; please enter it now", username
        )
        print('Enter your Jira API key:')
        keychain_item_password = getpass.getpass()

        # Store in keychain
        keyring.set_password(__name__, username, keychain_item_password)

    return keychain_item_password

api_token = read_keychain_password(username)
if not api_token:
    log.error(
        "API token not found for %s; see https://github.com/rpunt/jiracli/blob/main/README.md#authentication",
        username,
    )
    sys.exit(1)

JIRA_CLIENT = client.JiraClient(server, username, api_token)

__all__ = ["JIRA_CLIENT", "CONFIG", "log"]
