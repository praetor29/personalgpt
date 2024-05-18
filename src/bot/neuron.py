"""
message_handler
~~~~~~~~~~~~~~~
Handles on_message() functions.
"""

# Import libraries
import discord
from src.cognition.response import neural


async def reply(message: discord.Message):
    """
    Responds to the user message.
    """
    async with message.channel.typing():
        response = await neural(message=message)
        await message.reply(response)


async def send(message: discord.Message):
    """
    Responds to the user message.
    """
    async with message.channel.typing():
        response = await neural(message=message)
        await message.channel.send(response)
