'''
+---------------------------------------------------------------+
 This file contains useful functions for coding quality of life.
+---------------------------------------------------------------+
'''

import os
from constants import *

def clear():
    '''
    Clears the screen.
    '''
    os.system('cls' if os.name == 'nt' else 'clear')

def bot_mention_strip(message):
    '''
    Removes the bot's mention prefix and cleans up whitespace.
    '''
    mention = f'<@{BOT_ID}>'
    message_clean = message.removeprefix(mention).strip()
    return message_clean