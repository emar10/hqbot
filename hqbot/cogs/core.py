"""HQBot Core commands extension."""

from discord.ext import commands


class Core(commands.Cog):
    """HQBot Core commands Cog."""

    def __init__(self, bot):
        """Initialize Cog."""
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        """Test if the bot works, simply responds with 'Pong!'."""
        await ctx.send('Pong!')


def setup(bot):
    """Initialize the Extension."""
    bot.add_cog(Core(bot))
