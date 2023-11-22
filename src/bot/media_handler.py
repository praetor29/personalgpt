'''
media handler
~~~~~~~~~~~~~
Handles media analysis.
'''

# Import libraries
import discord
from src.core import constants
from src.cognition import cognition

async def verify_media(message: discord.Message) -> list:
    """
    Verifies if media is of a valid type. Returns list of verified attachments.
    """
    media = []

    for attachment in message.attachments:
        # Extract MIME info
        # - after normalizing to lowercase for safety
        # - splitting along /
        type, subtype = attachment.content_type.lower().split('/')

        # Check if MIME matches acceptable media and append/ignore
        if type in constants.MEDIA.keys() and subtype in constants.MEDIA[type]:
            media.append(attachment)

    return media                 

async def reply_media(message: discord.Message, media: list):
    """
    Responds to the user message. Also sends through media.
    """
    async with message.channel.typing():
        response = await cognition.response_media(message=message, media=media)
        await message.reply(response)