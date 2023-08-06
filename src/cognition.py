'''
+---------------------------------------------------------------+
 This file contains functions that interact with the OpenAI API. 
+---------------------------------------------------------------+
'''

import openai
import constants
import utility

openai.api_key = constants.OPENAI_API_KEY

async def chat_link(input: str, short_history: list) -> str:
    '''
    Communicates with the API asynchronously, and yields max char responses.
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
    uplink.append(
        {
            'role'    : 'user',
            'content' : input,
        }
    )

    downlink = await openai.ChatCompletion.acreate(
        model      = constants.MODEL_CHAT,
        messages   = uplink,
        stream     = True,
         # Fine-tuning:
        max_tokens = constants.CHAT_TOKEN_MAX,
        temperature = 1,
    )
    
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
                buffer = buffer[slice:]
        if buffer:
            yield buffer
    except KeyError:
        yield buffer
    except openai.error.OpenAIError:
        yield constants.ERROR_OPENAI