'''
+---------------------------------------------------------------+
 This file contains functions that interact with the OpenAI API. 
+---------------------------------------------------------------+
'''

import openai
import asyncio
import concurrent.futures
import constants
import utility

openai.api_key = constants.OPENAI_API_KEY
pool = concurrent.futures.ThreadPoolExecutor()


def chat_link(input: str, short_history: list) -> str:
    '''
    Communicates with the API on a separate thread.
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

    downlink = openai.ChatCompletion.create(
        model = constants.MODEL_CHAT,
        messages = uplink,

        # Fine-tuning:
        max_tokens = constants.CHAT_TOKEN_MAX,
        temperature = 1,
    )
    
    try:
        response = downlink['choices'][0]['message']['content']
    except (KeyError, openai.error.OpenAIError):
        response = constants.ERROR_OPENAI
    return response

async def chat_response(input: str, short_history: list) -> str:
    '''
    Sends the chat prompt + user_message to the API.
    '''
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(pool, chat_link, input, short_history)
    return response

'''
Allow per paragraph streaming (multiple messages)!
'''
