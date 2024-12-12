"""
utility
~~~~~~~
A collection of utility functions.
"""

r"""
██╗   ██╗████████╗██╗██╗     ██╗████████╗██╗   ██╗
██║   ██║╚══██╔══╝██║██║     ██║╚══██╔══╝╚██╗ ██╔╝
██║   ██║   ██║   ██║██║     ██║   ██║    ╚████╔╝ 
██║   ██║   ██║   ██║██║     ██║   ██║     ╚██╔╝  
╚██████╔╝   ██║   ██║███████╗██║   ██║      ██║   
 ╚═════╝    ╚═╝   ╚═╝╚══════╝╚═╝   ╚═╝      ╚═╝                                              
"""

# Import libraries
from os import system, name
import tiktoken
import discord
import re


def clear():
    """
    Clears the console screen using OS specific command.
    - Windows: 'cls'
    - POSIX  : 'clear'
    """
    system("cls" if name == "nt" else "clear")


async def tokenize(input: str) -> int:
    """
    Tokenize strings using tiktoken's 'cl100k_base'.
    Works with gpt-4 et al. and embeddings models.
    """
    encoding = tiktoken.get_encoding("cl100k_base").encode(input)
    tokens = len(encoding)
    return tokens


async def tokenize_lite(input: str) -> int:
    """
    Tokenize strings using a simple approximation:
    "1 token = 4 characters."
    """
    tokens = len(input) // 4
    return tokens


def get_channel_name(channel):
    """
    Helper function to determine the name of the channel.
    """
    if isinstance(channel, discord.DMChannel):
        return channel.recipient.name if channel.recipient else "UnknownDM"
    elif isinstance(channel, (discord.TextChannel, discord.Thread)):
        return channel.name
    else:
        return "UnknownChannel"


async def verify_media(message: discord.Message) -> list:
    """
    Verifies if media is a valid image. Returns a list of verified image attachments.

    Args:
        message: The Discord message to check.

    Returns:
        A list of verified image attachments.
    """

    # Acceptable Media (as of present implementation)
    MEDIA = {"image/png", "image/gif", "image/jpeg", "image/webp"}

    media = []

    for attachment in message.attachments:
        try:
            content_type = attachment.content_type.lower()

            # Use regex to match image MIME types
            if re.match(r"^image/", content_type):
                # Further check against specific MIME types for more precision
                if content_type in MEDIA:
                    media.append(attachment)
        except AttributeError as e:
            print(f"Error processing attachment: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    return media
