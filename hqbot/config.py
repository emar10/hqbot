"""HQBot configuration."""


import platform
import logging
import json
import dacite
from dataclasses import dataclass, field
from typing import Optional


logger = logging.getLogger(__name__)


class ConfigError(Exception):
    """Configuration related errors."""

    pass


@dataclass
class Config:
    """Global configuration data structure."""

    token: str
    test_guild: Optional[int]
    extensions: list[str] = field(default_factory=lambda: ['core'])


def load_config() -> Config:
    """Attempt to load a configuration and return the result."""
    logger.info('Loading configuration file...')
    plat = platform.system()
    paths = list()

    paths.append('.')

    logger.debug('Trying to detect config path for OS...')
    if plat == 'Linux':
        logger.debug('Detected Linux, using \'/etc/hqbot/hqbot.json\'.')
        paths.append('/etc/hqbot')
    elif plat == 'Windows':
        logger.debug('Detected Windows, using '
                     '\'/Program Data/hqbot/hqbot.json\'.')
        paths.append('/Program Data/hqbot')
    else:
        logger.warning('Could not detect OS, only searching current directory '
                       'for config.')

    for path in paths:
        try:
            logger.debug(f'Trying to load configuration from \'{path}\'...')
            file = open(f'{path}/hqbot.json', 'r')
            data = json.load(file)
            config = dacite.from_dict(Config, data)
            logger.info(f'Loaded configuration from \'{path}/hqbot.json\'.')
            return config
        except OSError as e:
            logger.debug(f'Failed to open  \'{path}\': {e}')
        except dacite.DaciteError as e:
            logger.critical(f'Failed to load configuration from \'{path}\': '
                            f'{e}')
            raise ConfigError

        logger.critical('Could not find any configuration file!')
        raise ConfigError
