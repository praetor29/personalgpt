'''
+---------------------------------------------------------------+
 This file contains useful functions for coding quality of life.
+---------------------------------------------------------------+
'''

import os
from constants import *
import datetime
from pytz import timezone

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

def current_date():
    '''
    Fetches current US/Central date and time in M, D, Y, H:M:S
    '''
    value = datetime.datetime.now(timezone('US/Central')).strftime("%A, %B %d, %Y, %I:%M %p")
    return value
