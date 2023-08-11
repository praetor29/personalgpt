'''
+---------------------------------------------------------------+
 This file contains useful functions for coding quality of life.
+---------------------------------------------------------------+
'''

import os
import constants
import sys
from datetime import datetime, timezone
import tiktoken

def clear() -> None:
    '''Clears the screen.'''
    os.system('cls' if os.name == 'nt' else 'clear')

def current_date() -> str:
    '''
    Fetches current UTC date and time in M, D, Y, H:M
    '''
    try:
        value = datetime.now(timezone.utc).strftime("%A, %B %d, %Y, %I:%M %p")
    except Exception:
        print('utility.current_date() failure. Returning empty string.')
        value = str()
    return value

# def sql_date(timestamp) -> str:
#     '''
#     Converts current_date() timestamp into SQL acceptable format.
#     '''
#     try:
#         datetime_obj  = datetime.strptime(timestamp, "%A, %B %d, %Y, %I:%M %p")
#         sql_timestamp = datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
#     except Exception:
#         print('utility.sql_date() failure. Returning empty string.')
#         sql_timestamp = str()
#     return sql_timestamp

def tokenizer(input, model) -> int:
    '''
    Calculates number of tokens in the input.
    '''
    try:
        if model is None:
            encoding = tiktoken.get_encoding('cl100k_base')
        else:
            try: # Set encoding
                encoding = tiktoken.encoding_for_model(model)
            except KeyError or AttributeError:
                print('Warning: Encoding model not found. Defaulting to cl100k_base.')
                encoding = tiktoken.get_encoding('cl100k_base')
        
        # Calcualtion for others
        if not model in { 
            'gpt-4',
            'gpt-4-32k',
            'gpt-3.5-turbo',
            'gpt-3.5-turbo-16k',
        }:
            tokens = len(encoding.encode(input))
            return tokens

        # Calculation for GPT models
        else: 
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
    except:
        print('utility.tokenizer() failure. Calling sys.exit()')
        sys.exit()
    
def splitter(input: str) -> list:
    '''
    Splits a string into a list of strings
    of 2000 characters max without breaking words.
    '''
    words = input.split(' ')
    capsule = []
    packet = ''

    for word in words:
        if len(packet + word + ' ') > constants.DISCORD_CHAR_MAX:
            # Add packet
            capsule.append(packet)
            # Create new packet
            packet = word + ' '
        else:
            # Add words to packet
            packet += word + ' '

    # Add the last message if not empty
    if packet:
        capsule.append(packet)

    return capsule
