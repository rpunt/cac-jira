# pylint: disable=broad-except
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

default_config = {}
default_config_dir = os.path.join(os.path.dirname(__file__), 'config')
default_config_file = os.path.join(default_config_dir, f"{__name__}.yaml")
if os.path.exists(default_config_file):
    with open(default_config_file, 'r', encoding='utf-8') as f:
        default_config.update(yaml.safe_load(f))
config = cac.config.load(__name__, default_config)

log.debug("user config path: %s", config['config_file_path'])

server = config.get('server', 'INVALID_DEFAULT').replace('https://', '')
if config['server'] == 'INVALID_DEFAULT':
    log.error("Invalid server in %s: %s", config['config_file_path'], server)
    sys.exit(1)

username = config.get('username', 'INVALID_DEFAULT')
if config['username'] == 'INVALID_DEFAULT':
    log.error("Invalid username in %s: %s", config['config_file_path'], username)
    sys.exit(1)

api_token = keyring.get_password("cac-jira", username)
if not api_token:
    log.error("API token not found for %s", username)
    sys.exit(1)

JIRA_CLIENT = client.JiraClient(server, username, api_token)

__all__ = ["JIRA_CLIENT", "log"]
