"""HQBot bot class module."""

import logging

import discord
from discord_slash import SlashCommand
from discord.ext import commands

from hqbot.config import Config, load_config

logger = logging.getLogger(__name__)


class HqBot(commands.Bot):
    """Main bot class."""

    config: Config
    slash: SlashCommand

    def __init__(self):
        """Initialize the bot."""
        logger.info('Initializing HqBot...')

        self.config = load_config()

        logger.debug('Doing discord.py init...')
        super().__init__(command_prefix='/', help_command=None,
                         intents=discord.Intents.default())

        logger.debug('Doing discord-py-interactions init...')
        self.slash = SlashCommand(self, sync_commands=True,
                                  debug_guild=self.config.test_guild)

        logger.info('Loading extensions...')
        for ext in self.config.extensions:
            logger.debug(f'Loading extension \'{ext}\'...')
            self.load_extension(f'{__package__}.cogs.{ext}')
        logger.debug('Done loading extensions.')

        logger.info('Done initializing HqBot.')

    def run(self):
        """Run the bot."""
        super().run(self.config.token)
