import yaml
from pathlib import Path

from src.exceptions import ConfigError
from config.const import *


default_log_filename = f"{PROJECT_NAME.lower()}"
project_root_dir = Path(__file__).parent.parent

# If you want to run teleshares without docker, I advice you to create "config-dev.yaml" and run it with --dev arg

_CONFIG_FILENAME = "config.yaml"


try:
    cfg = yaml.safe_load(open(f"{project_root_dir}/config/{_CONFIG_FILENAME}", 'r'))
except FileNotFoundError:
    raise ConfigError


if cfg['plugins']['gateways']:
    try:
        gateways_info = yaml.safe_load(open(f"{project_root_dir}/config/gateways.yaml", 'r'))
    except FileNotFoundError:
        raise ConfigError
else:
    gateways_info = None

if cfg['plugins']['wallet']:
    try:
        wallet_data = yaml.safe_load(open(f"{project_root_dir}/config/wallet.yaml", 'r'))
    except FileNotFoundError:
        raise ConfigError
else:
    wallet_data = None


# Used in aiopg.sa
pg_config = cfg['postgres']

# Used in alembic
SQL_CONN_URL = f"postgres+psycopg2://{pg_config['user']}:{pg_config['password']}" \
               f"@" \
               f"{pg_config['host']}:{pg_config['port']}/{pg_config['database']}"

nodes = cfg['bitshares']['nodes']
