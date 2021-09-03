"""Voice/Music extension."""

from collections import deque
from dataclasses import dataclass
import logging
from typing import Any, Optional

import discord
from discord.voice_client import VoiceClient
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option
import youtube_dl

from hqbot.hqbot import HqBot


logger = logging.getLogger(__name__)


class MusicError(Exception):
    """Exception for the Music cog."""


@dataclass
class Track:
    """A track that can be played by the bot."""

    filename: str
    title: str


class GuildPlayer:
    """Player for a specific Guild."""

    guild: discord.Guild
    track_queue: deque[Track]
    track_current: Optional[Track]
    voice: Optional[VoiceClient]

    def __init__(self, guild: discord.Guild):
        """Initialize the player instance."""
        self.guild = guild
        self.track_queue = deque()
        self.track_current = None
        self.voice = None

    async def connect(self, channel: discord.VoiceChannel):
        """Connect to the specified voice channel."""
        logger.debug(f'Joining channel \'{channel}\'...')
        self.voice = await channel.connect()

    async def auto_connect(self, member: discord.Member):
        """Automatically connect to the specified user's channel."""
        logger.debug(f'Joining channel of \'{member}\'...')
        await self.connect(member.voice.channel)

    async def disconnect(self):
        """Disconnect from the current voice channel."""
        self.track_queue.clear()
        self.track_current = None

        if self.voice:
            await self.voice.disconnect()
            self.voice = None

    def add_track(self, track: Track,
                  requester: Optional[discord.Member] = None):
        """Add a track to the queue. Begins playing if possible."""
        logger.debug(f'Adding track with URL \'{track.filename}\'.')
        self.track_queue.append(track)

        if self.voice and not self.voice.is_playing():
            logger.debug('Auto-starting playback...')
            self.pop_track()

    def pop_track(self):
        """Play the next track in the queue."""
        if len(self.track_queue) > 0:
            self.track_current = self.track_queue.popleft()
            source = discord.FFmpegOpusAudio(self.track_current.filename)

            def play_next(_: Exception):
                self.pop_track()

            self.voice.play(source, after=play_next)
        else:
            self.voice.loop.create_task(self.disconnect())


class Music(commands.Cog):
    """Cog of Music-related functionality."""

    bot: HqBot
    players: dict[discord.Guild, GuildPlayer]
    ytdl: youtube_dl.YoutubeDL
    ytdl_options: dict[str, Any] = {
        'format': 'bestaudio/best',
        'default_search': 'auto',
        'source_address': '0.0.0.0'
    }

    def __init__(self, bot: HqBot):
        """Initialize the cog."""
        self.bot = bot
        self.players = dict()
        self.ytdl = youtube_dl.YoutubeDL(self.ytdl_options)

    def get_player(self, guild: discord.Guild) -> GuildPlayer:
        """Get the GuildPlayer for the specified Guild."""
        if guild not in self.players:
            self.players[guild] = GuildPlayer(guild)
            logger.info(f'Created new player for guild \'{guild}\'.')

        return self.players[guild]

    @cog_ext.cog_slash(options=[
        create_option(
            name='query',
            description='URL or search term.',
            option_type=3,
            required=True
        )
    ])
    async def play(self, ctx: SlashContext, query: str):
        """Play music from the provided link or search query."""
        logger.debug(f'{ctx.author} invoked Play with query \'{query}\'')

        if not (query.startswith('https://') or query.startswith('http://')):
            logger.debug('Interpreting query as a search.')
            query = f'ytsearch:{query}'
        result = self.ytdl.extract_info(query, download=False)

        if 'entries' in result:
            logger.debug('YTDL result appears to be a playlist, using first '
                         'result.')
            result = result['entries'][0]
        track = Track(result['url'], result['title'])

        player = self.get_player(ctx.guild)
        if not player.voice:
            if ctx.author.voice:
                await player.auto_connect(ctx.author)
            else:
                await ctx.reply('You are not in a voice channel!')
                return
        player.add_track(track)

        await ctx.reply(f'Added *{track.title}* to the queue.')

    @cog_ext.cog_slash()
    async def skip(self, ctx: SlashContext):
        """Skip the currently playing track."""
        logger.debug(f'{ctx.author} invoked Skip.')

        player = self.get_player(ctx.guild)
        if not player.voice:
            await ctx.reply('Nothing is playing right now!')
        else:
            player.voice.stop()
            await ctx.reply('Skipped the current track.')

    @cog_ext.cog_slash()
    async def stop(self, ctx: SlashContext):
        """Stop playback and disconnect from the current voice channel."""
        logger.debug(f'{ctx.author} invoked Stop.')

        player = self.get_player(ctx.guild)
        if not player.voice:
            await ctx.reply('Nothing is playing right now!')
        else:
            await player.disconnect()
            await ctx.reply('Stopped playback.')


def setup(bot: HqBot):
    """Initialize the extension."""
    bot.add_cog(Music(bot))
