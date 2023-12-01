'''
chat.py
~~~~~~~
Asynchronous Audio Chat Completion functionality.
'''

# Import libraries
import openai
from src.core import constants
from src.memory import memory, custom_message

async def constructor(message: custom_message.AudioMessage) -> list:
    """
    Constructs the uplink list.
    """
    # Construct system prompt
    uplink = [
            {
                'role'    : 'system',
                'content' : constants.VOICE_PROMPT,
            },
    ]

    # Fetch conversation context from memory queue
    context = await memory.unravel(message=message)
    # Augment uplink with context
    uplink.extend(context)

    return uplink


async def chat_completion_audio(client: openai.AsyncOpenAI, message: custom_message.AudioMessage) -> str:
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