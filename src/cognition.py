'''
+---------------------------------------------------------------+
 This file contains functions that interact with the OpenAI API. 
+---------------------------------------------------------------+
'''

import openai
import asyncio
import concurrent.futures
import constants
from utility import current_date

openai.api_key = constants.OPENAI_API_KEY
pool = concurrent.futures.ThreadPoolExecutor()


def chat_link(input: str) -> str:
    '''
    Communicates with the API on a separate thread.
    '''
    date_line = f'{current_date()} CDT.'

    downlink = openai.ChatCompletion.create(
        model = constants.MODEL_CHAT,
        messages = [
            {
                'role' : 'system',
                'content' : f'{constants.PROMPT_CHAT}\n{date_line}',
            },
            {
                'role' : 'user',
                'content' : input
            },
        ],
        # Fine-tuning goes here
        max_tokens = constants.CHAT_TOKEN_MAX,
        temperature = 1,
    )
    
    try:
        response = downlink['choices'][0]['message']['content']
    except (KeyError, openai.error.OpenAIError):
        response = constants.ERROR_OPENAI
    return response

async def chat_response(input: str) -> str:
    '''
    Sends the chat prompt + user_message to the API.
    '''
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(pool, chat_link, input)
    return response



'''
Allow per paragraph streaming (multiple messages)!
'''
