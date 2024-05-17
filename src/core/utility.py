"""
utility
~~~~~~~
A collection of utility functions.
"""

"""
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
    elif isinstance(channel, discord.TextChannel):
        return channel.name
    else:
        return "channel"

