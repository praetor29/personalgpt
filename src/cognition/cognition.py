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

# TODO: Convert to OOP Class Structure

# Import libraries
import discord
from openai import AsyncOpenAI
from typing import Union, List

# Import modules
from src.core import constants
from src.cognition import chat, chat_media, chat_audio, whisper
from src.memory import custom_message

# Initialize client with openai key
client = AsyncOpenAI(api_key=constants.OPENAI)

async def response(message: discord.Message) -> str:
    """
    Front-end for a chat completion.
    """
    response = await chat.chat_completion(client=client, message=message)
    return response

async def response_media(message: discord.Message, media: list) -> Union[str, List]:
    """
    Front-end for a chat completion with media content.
    """
    response, media_context = await chat_media.chat_completion_media(client=client, message=message, media=media)  

    return response, media_context

async def response_audio(message: custom_message.AudioMessage) -> str:
    """
    Front-end for an audio chat completion.
    """
    response = await chat_audio.chat_completion_audio(client=client, message=message)
    return response

async def transcribe(audio) -> str:
    """
    Front-end for an audio transcription.
    """
    transcription = await whisper.whisper(client=client, audio=audio)
    return transcription