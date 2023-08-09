'''
+---------------------------------------------------------------+
 This file contains functions that interact with the OpenAI API. 
+---------------------------------------------------------------+
'''

import openai
import constants
import utility
from errors.handler import handle_exception

openai.api_key = constants.OPENAI_API_KEY

async def chat_link(message: str, nametag: str, short_history: list) -> str:
    '''
    Communicates with the API asynchronously, and yields max char responses.

    message   = cleaned message.content
    nametag   = message.author.display_name said:
    short_history  = snapshot of ShortTermMemory channel-specific queue
    '''
    # day/date/time context.
    date_line = f'It is currently {utility.current_date()} {constants.TIMEZONE}.'
    
    # Initializes uplink
    uplink = [
            {
                'role'    : 'system',
                'content' : constants.PROMPT_CHAT,
            },
            {
                'role'    : 'system',
                'content' : date_line,
            },
    ]
    # Extends uplink with short history
    uplink.extend(short_history)
    # Finalizes uplink with user input
    uplink.extend([
        {
            'role'    : 'system',
            'content' : nametag,
        },
        {
            'role'    : 'user',
            'content' : message,
        },
    ])

    # OpenAI API Request
    try:
        downlink = await openai.ChatCompletion.acreate(
            model      = constants.MODEL_CHAT,
            messages   = uplink,
            stream     = True,
            # Fine-tuning:
            max_tokens = constants.CHAT_TOKEN_MAX,
            temperature = constants.CHAT_TEMP,
        )
    except Exception as exception:
        yield (f"## `Error`\n```vbnet\n{handle_exception(exception)}\n```")
    
    buffer = ''
    try:
        async for chunk in downlink:
            buffer += chunk['choices'][0]['delta']['content']
            # Yield at max characters
            while len(buffer) >= constants.DISCORD_CHAR_MAX:
                # Find the nearest whole paragraph to CHAR_MAX
                slice = buffer.rfind('\n\n', 0, constants.DISCORD_CHAR_MAX)
                # If no paragraph break found
                if slice == -1:
                    slice = constants.DISCORD_CHAR_MAX
                yield buffer[:slice]
                print(buffer)
                buffer = buffer[slice:]
        if buffer:
            yield buffer
    except KeyError:
        yield buffer
    except Exception as exception:
        yield (f"## `Error`\n```vbnet\n{handle_exception(exception)}\n```")

async def embed(message: str) -> list:
    '''
    Convert message into a 1536 dimensional vector.
    Uses the OpenAI Embeddings API.
    '''
    try:
        # API Call
        response = await openai.Embedding.acreate(
                    input = message,
                    model = constants.MODEL_EMBED,
                )
        # Retrieving embedding
        vector = response["data"][0]["embedding"]
        return vector
    
    # If embedding fails (? Rethink this logic)
    except Exception as exception:
        print(f'cognition.embed() failure. Returning [].\n{handle_exception(exception)}')
        return []
