'''
cognition
~~~~~~~~~
Cognitive functions using API requests.
'''
'''
 ██████╗ ██████╗  ██████╗ ███╗   ██╗██╗████████╗██╗ ██████╗ ███╗   ██╗
██╔════╝██╔═══██╗██╔════╝ ████╗  ██║██║╚══██╔══╝██║██╔═══██╗████╗  ██║
██║     ██║   ██║██║  ███╗██╔██╗ ██║██║   ██║   ██║██║   ██║██╔██╗ ██║
██║     ██║   ██║██║   ██║██║╚██╗██║██║   ██║   ██║██║   ██║██║╚██╗██║
╚██████╗╚██████╔╝╚██████╔╝██║ ╚████║██║   ██║   ██║╚██████╔╝██║ ╚████║
 ╚═════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝                                                                                                                                  
'''

# Import libraries
import discord
from openai import AsyncOpenAI
# Import modules
from src.core import constants
from src.cognition import chat

# Initialize client with openai key
client = AsyncOpenAI(api_key=constants.OPENAI)

async def response(message: discord.Message) -> str:
    """
    Front-end for a chat completion.
    """
    response = await chat.chat_completion(client=client, message=message)
    return response

