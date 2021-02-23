"""A general-purpose bot for Discord."""

import platform
import sys
import discord
import yaml
import os
from discord.ext import commands
from importlib.util import resolve_name


def get_default_config() -> str:
    """Determine the appropriate default configuration file."""
    plat = platform.system()
    paths = list()

    if plat == 'Linux':
        paths.append('/etc/hqbot')
    elif plat == 'Windows':
        paths.append('/Program Data/hqbot')

    paths.append('.')

    for path in paths:
        if os.path.isfile(f'{path}/hqbot.json'):
            return f'{path}/hqbot.json'

    return None


def load_config(path: str = None):
    """Load the provided configuration file or load the default config."""
    path = path or get_default_config()
    if path is None:
        return dict()

    config_file = open(path, 'r')
    config = yaml.safe_load(config_file)

    return config


class HqBot(commands.Bot):
    """Main HQBot driver class."""

    def __init__(self):
        """Initialize the bot."""
        self.config = load_config()
        if 'token' not in self.config:
            print('Config does not include a token, cannot proceed!',
                  file=sys.stderr)
            raise Exception

        intents = discord.Intents.default()
        # intents.members = True
        super().__init__(command_prefix='!', intents=intents)

        for ext in self.config['extensions']:
            try:
                self.load_extension(resolve_name(ext, __package__))
            except Exception as e:
                print(f'Failed to load extension \'{ext}\'.', file=sys.stderr)
                raise e

    def run(self):
        """Run the bot."""
        super().run(self.config['token'], reconnect=True)
