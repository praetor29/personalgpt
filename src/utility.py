'''
+---------------------------------------------------------------+
 This file contains useful functions for coding quality of life.
+---------------------------------------------------------------+
'''

import os
from constants import *
import datetime
from pytz import timezone
import tiktoken

def clear() -> None:
    '''Clears the screen.'''
    os.system('cls' if os.name == 'nt' else 'clear')

def bot_mention_strip(message: str) -> str:
    '''
    Removes the bot's mention prefix and cleans up whitespace.
    '''
    mention = f'<@{BOT_ID}>'
    message_clean = message.removeprefix(mention).strip()
    return message_clean

def current_date() -> str:
    '''
    Fetches current US/Central date and time in M, D, Y, H:M:S
    '''
    value = datetime.datetime.now(timezone('US/Central')).strftime("%A, %B %d, %Y, %I:%M %p")
    return value

def tokenizer(input: str, model: str) -> int:
    '''
    Calculates number of tokens in the input.
    '''

    try: # Set encoding
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print('Warning: Encoding model not found. Defaulting to cl100k_base.')
        encoding = tiktoken.get_encoding('cl100k_base')
    
    # Calculation for GPT models
    if model in { 
        'gpt-4',
        'gpt-4-32k',
        'gpt-3.5-turbo',
        'gpt-3.5-turbo-16k',
    }:
        tokens_per_message = 3
        tokens_per_name = 1

        tokens = 0
        for message in input:
            tokens += tokens_per_message
            for key, value in message.items():
                tokens += len(encoding.encode(value))
                if key == "name":
                    tokens += tokens_per_name
        tokens += 3
        return tokens

    # Calcualtion for others
    else: 
        tokens = len(encoding.encode(input))
        return tokens

