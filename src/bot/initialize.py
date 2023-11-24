'''
initialize
~~~~~~~~~~
Handles on_ready() functions.
'''

# Import libraries
import discord
from src.core import constants, ascii

async def print_ascii():
    """
    Print ASCII art in terminal.
    """
    print(ascii.bot_2)

async def set_presence(bot: discord.Bot):
    """
    Change presence to what's defined in config.
    """
    await bot.change_presence(
        status   = constants.STATUS,
        activity = discord.Activity(
        type     = constants.ACTIVITY_TYPE,
        name     = constants.ACTIVITY_NAME,
        )
    )