"""HQBot command line module."""

from hqbot.hqbot import HqBot
import logging


logger = logging.getLogger(__name__)


def run():
    """Package entry point."""
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('discord').setLevel(logging.WARNING)
    bot = HqBot()
    bot.run()
