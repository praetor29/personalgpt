'''
chat.py
~~~~~~~
Asynchronous Chat Completion functionality.
'''

# Import libraries
import openai
import discord
from src.core import constants
from src.memory import memory

async def constructor(message: discord.Message) -> list:
    """
    Constructs the uplink list.
    """
    # Construct system prompt
    uplink = [
            {
                'role'    : 'system',
                'content' : constants.CHAT_PROMPT,
            },
    ]

    # Fetch conversation context from memory queue
    context = await memory.unravel(message=message)
    # Augment uplink with context
    uplink.extend(context)

    return uplink


async def chat_completion(client: openai.AsyncOpenAI, message: discord.Message) -> str:
    """
    Sends and receives a response from the OpenAI API.
    """
    # Construct uplink
    uplink = await constructor(message=message)

    response = await client.chat.completions.create(
        messages    = uplink,
        model       = constants.CHAT_MODEL,
        temperature = constants.CHAT_TEMP,
        max_tokens  = constants.CHAT_MAX,
    )

    return response.choices[0].message.content