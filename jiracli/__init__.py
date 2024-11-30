import cac_core as cac
from importlib import metadata

try:
    __version__ = metadata.version(__package__)
except Exception:
    __version__ = "#N/A"

import jiracli.core.client as client
import keyring

log = cac.logger.new(__name__)
log.debug(f"Initializing {__name__} version {__version__}")

config = cac.config.load(__name__)

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
