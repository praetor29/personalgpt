'''
+----------------------------------------------------------+
 This file contains constants for the Personal GPT project.
+----------------------------------------------------------+
'''

import os
import dotenv
dotenv.load_dotenv()

# PATHS
CHAT_PROMPT_PATH = os.path.join('cogs', 'prompt.txt')
MEMORY_DB_PATH   = os.path.join('data', 'memory.db')

# API keys/tokens
OPENAI_API_KEY    = os.getenv('OPENAI_API_KEY')
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
DISCORD_BOT_ID    = os.getenv('DISCORD_BOT_ID')

# OpenAI Models
MODEL_EMBED     = 'text-embedding-ada-002'
MODEL_SUMMARIZE = 'text-curie-001'
MODEL_CHAT      = 'gpt-3.5-turbo'

# Error Messages
ERROR_CONTACT    = '`Please contact` <@704328610567159918> `if the problem persists.`'

'''Prompts'''

# Model Chat
SONG     = 'Can You Hear The Music (Ludwig Göransson)'
TIMEZONE = 'UTC'

with open(CHAT_PROMPT_PATH, 'r', encoding='utf-8') as chat_prompt:
    PROMPT_CHAT = chat_prompt.read().format(SONG=SONG)

'''Tokens'''
LONG_MEM_MAX     = 900
SHORT_MEM_MAX    = 500
# Controls how often trim() is called.
UPPER_THRESHOLD  = 0.90 
LOWER_THRESHOLD  = 0.50

CHAT_TOKEN_MAX   = 450
DISCORD_CHAR_MAX = 1500
