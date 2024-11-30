import cac_core as cac
from importlib import metadata
import os
import yaml

try:
    __version__ = metadata.version(__package__)
except Exception:
    __version__ = "#N/A"

import jiracli.core.client as client
import keyring

log = cac.logger.new(__name__)
log.debug(f"Initializing {__name__} version {__version__}")

default_config = {}
default_config_dir = os.path.join(os.path.dirname(__file__), 'config')
default_config_file = os.path.join(default_config_dir, f"{__name__}.yaml")
if os.path.exists(default_config_file):
    with open(default_config_file, 'r') as f:
        default_config.update(yaml.safe_load(f))
config = cac.config.load(__name__, default_config)

log.info(f"user config path: {config['config_file_path']}")

server = config.get('server', 'INVALID_DEFAULT').replace('https://', '')
if config['server'] == 'INVALID_DEFAULT':
    log.error(f"Invalid server in {config['config_file_path']}: {server}")
    exit(1)

username = config.get('username', 'INVALID_DEFAULT')
if config['username'] == 'INVALID_DEFAULT':
    log.error(f"Invalid username in {config['config_file_path']}: {username}")
    exit(1)

api_token = keyring.get_password("cac-jira", username)
if not api_token:
    log.error(f"API token not found for {username}")
    exit(1)

JIRA_CLIENT = client.JiraClient(server, username, api_token)
