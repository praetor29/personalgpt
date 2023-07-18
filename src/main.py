'''
+------------------------------------------------------------------+
| Title      : Personal GPT                                        |
| Author     : Pranav Chiploonkar (@praetor29)                     |
| Date       : 17 July 2023                                        |
+------------------------------------------------------------------+
| Description: This program runs the core loop of the discord bot. |
+------------------------------------------------------------------+
'''

'''
Agenda:

1. Implement chat memory capabilities (per server DB). Must constantly embed to grow DB.
2. Implement 'short term memory' = (relevant info from embed) + (5 recent texts - depending on tokens)
3. Implement functions [like weather](https://platform.openai.com/docs/guides/gpt/function-calling)
4. Implement slash commands that allow changing prompts? Maybe create thread where ping not needed.
5. Encrypt text before storage for privacy policy.

'''

# Import functions and constants
from constants import *
from utility import *

print("Hello")

