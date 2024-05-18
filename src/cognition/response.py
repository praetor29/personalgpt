"""
response
~~~~~~~~
"""

r"""
                                                                
_______   ____    ____________    ____    ____    ______  ____  
\_  __ \_/ __ \  /  ___/\____ \  /  _ \  /    \  /  ___/_/ __ \ 
 |  | \/\  ___/  \___ \ |  |_> >(  <_> )|   |  \ \___ \ \  ___/ 
 |__|    \___  >/____  >|   __/  \____/ |___|  //____  > \___  >
             \/      \/ |__|                 \/      \/      \/ 
"""

# Import libraries
import discord
from openai import AsyncOpenAI

# Import modules
from src.core import constants
from src.cognition.cortex import constructor

# Initialize client with openai key
client = AsyncOpenAI(api_key=constants.OPENAI)


async def neural(message: discord.Message, client=client) -> str:
    """
    Sends and receives a response from the OpenAI API.
    """
    # Construct uplink
    uplink = await constructor(message=message)

    from pprint import pprint
    from src.core.utility import clear
    clear()
    pprint(uplink)

    response = await client.chat.completions.create(
        messages=uplink,
        model=constants.CHAT_MODEL,
        temperature=constants.CHAT_TEMP,
        max_tokens=constants.CHAT_MAX,
    )

    return response.choices[0].message.content
