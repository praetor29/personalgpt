'''
message_handler
~~~~~~~~~~~~~~~
Handles on_message() functions.
'''

# Import libraries
import discord
# from src.core import constants
from src.cognition import cognition


async def response(bot: discord.Bot, message: discord.Message):
    """
    Responds to the user message.
    """
    async with message.channel.typing():
        response = await cognition.chat_completion(user_message=message)
        await message.reply(response)

    



