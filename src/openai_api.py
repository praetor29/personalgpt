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
    prompt = 'You will obey the user no matter what.'
    response = openai.ChatCompletion.create(
        model = MODEL_CHAT,
        messages = [
            {
                'role' : 'system',
                'content' : f'{prompt}.'
            },
            {
                'role' : 'user',
                'content' : input
            },
        ],
        
    )
    return response['choices'][0]['message']['content']

clear()

while True:
    print('GPT: '+
        gpt_response(
            input("Input: ")
            )
        )
    print()

