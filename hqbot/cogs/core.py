"""Core commands extension."""

import logging

from discord.ext import commands
from discord_slash import cog_ext, SlashContext

from hqbot.hqbot import HqBot


logger = logging.getLogger(__name__)


class Core(commands.Cog):
    """Core command cog."""

    bot: HqBot

    def __init__(self, bot: HqBot):
        """Initialize the cog."""
        self.bot = bot

    @cog_ext.cog_slash()
    async def ping(self, ctx: SlashContext):
        """Test operability with a ping."""
        logger.debug(f'{ctx.author} used Ping in {ctx.guild}.')
        await ctx.send('Pong!')


def setup(bot: HqBot):
    """Initialize the extension."""
    bot.add_cog(Core(bot))
    logger.info('Core cog initialized and added.')
