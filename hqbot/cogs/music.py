"""HQBot Voice/Music extension."""

import asyncio
import youtube_dl
import discord

from ..hqbot import HqBot
from discord.ext import commands


class YTDLSource(discord.FFmpegOpusAudio):
    """An audio source utilizing a youtube-dl stream."""

    ytdl_format_options = {
        'format': 'bestaudio/best',
        'outtmpl': '/tmp/hqbot/%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0'
    }

    ffmpeg_options = {
        'options': '-vn'
    }

    ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

    def __init__(self, data, *args, **kwargs):
        """Source initialization."""
        super().__init__(*args, **kwargs)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        """Create and return a new YTDLSource."""
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: cls.ytdl.extract_info(
            url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else cls.ytdl.prepare_filename(data)
        return cls(data, filename, **cls.ffmpeg_options)


class Music(commands.Cog):
    """HQBot Music cog."""

    def __init__(self, bot):
        """Cog initialization."""
        self.bot = bot

    @commands.command()
    async def play(self, ctx, *, url):
        """Play music from the provided link."""
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop,
                                               stream=True)
            ctx.voice_client.play(player)

        await ctx.send(f'Now playing: {player.title}')

    @commands.command()
    async def stop(self, ctx):
        """Stop the currently playing song."""
        await ctx.voice_client.disconnect()

    @play.before_invoke
    async def ensure_voice(self, ctx):
        """Attempt to automatically join a voice channel if not active."""
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send('You are not connected to a voice channel!')
                raise commands.CommandError('Author not connected to voice.')


def setup(bot: HqBot):
    """Initialize the Extension."""
    bot.add_cog(Music(bot))
