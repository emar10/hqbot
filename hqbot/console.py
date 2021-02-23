"""HQBot command-line entry point."""

from .hqbot import HqBot


def run():
    """Execute the bot."""
    bot = HqBot()

    try:
        bot.run()
    except KeyboardInterrupt:
        print('Caught SIGINT, going down...')
        bot.close()
        exit()
