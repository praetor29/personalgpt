'''
+---------------------------------------------------------------+
 This file contains functions that interact with the OpenAI API. 
+---------------------------------------------------------------+
'''

import openai
from constants import *

openai.api_key = OPENAI_API_KEY

def chat_response(input):
    response = openai.ChatCompletion.create(
        model = MODEL_CHAT,
        messages = [
            {
                'role' : 'system',
                'content' : f'{CHAT_PROMPT}.'
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