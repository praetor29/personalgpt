'''
+---------------------------------------------------------------+
 This file contains functions that interact with the OpenAI API. 
+---------------------------------------------------------------+
'''

import openai
from constants import *
from utility import current_date

openai.api_key = OPENAI_API_KEY

def chat_response(input):
    date_line = f'It is currently {current_date()} US/Central.'

    response = openai.ChatCompletion.create(
        model = MODEL_CHAT,
        messages = [
            {
                'role' : 'system',
                'content' : f'{PROMPT_CHAT}\n{date_line}',
            },
            {
                'role' : 'user',
                'content' : input
            },
        ],
        # Fine-tuning goes here
        max_tokens = CHAT_TOKEN_MAX,
        temperature = 1,
        stream = True
    )
    
    stream = []
    for chunk in response:
        try:
            stream.append(chunk['choices'][0]['delta']['content'])
        except:
            KeyError

    assembled = ''.join(stream)
    return assembled