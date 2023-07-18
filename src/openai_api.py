'''
+---------------------------------------------------------------+
 This file contains functions that interact with the OpenAI API. 
+---------------------------------------------------------------+
'''

import openai
from constants import *
from utility import *

openai.api_key = OPENAI_API_KEY


# Testing

def gpt_response(input):
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
        max_tokens = 490,
        temperature = 1,
    )
    return response['choices'][0]['message']['content']

clear()

while True:
    print('GPT: '+
        gpt_response(
            input("Input: ")
            )
        )

