'''
+----------------------------------------------------------+
 This file contains constants for the Personal GPT project.
+----------------------------------------------------------+
'''

import os
import dotenv
import discord
dotenv.load_dotenv()

# PATHS
CHAT_PROMPT_PATH       = os.path.join('data', 'prompt', 'prompt.txt')
TOPIC_PROMPT_PATH      = os.path.join('data', 'prompt', 'topic.txt')
HISTORICAL_PROMPT_PATH = os.path.join('data', 'prompt', 'historical.txt')
MEMORY_DB_PATH         = os.path.join('data', 'memory', 'database')
MEMORY_VECTOR_PATH     = os.path.join('data', 'memory', 'vectors')

# API keys/tokens
OPENAI_API_KEY    = os.getenv('OPENAI_API_KEY')
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
DISCORD_BOT_ID    = os.getenv('DISCORD_BOT_ID')

# OpenAI Models
MODEL_EMBED      = 'text-embedding-ada-002'
VECTOR_LENGTH    = 1536
ANNOY_TREES      = 20
MODEL_TOPIC      = 'text-curie-001'
MODEL_CHAT       = 'gpt-4'
MODEL_HISTORICAL = 'gpt-3.5-turbo'

# Error Messages
ERROR_CONTACT    = '`Please contact` <@704328610567159918> `if the problem persists.`'

'''Prompts'''

# Model Chat
NAME          = 'Stacy Evans'
TIMEZONE      = 'UTC'

STATUS        = discord.Status.idle
ACTIVITY_TYPE = discord.ActivityType.playing
ACTIVITY_NAME = 'Global Thermonuclear War'

with open(CHAT_PROMPT_PATH, 'r', encoding='utf-8') as chat_prompt:
    PROMPT_CHAT = chat_prompt.read().format(name=NAME)

# Topic Finder
with open(TOPIC_PROMPT_PATH, 'r', encoding='utf-8') as topic_prompt:
    PROMPT_TOPIC = topic_prompt.read()

# Historical Context
with open(HISTORICAL_PROMPT_PATH, 'r', encoding='utf-8') as historical_prompt:
    PROMPT_HISTORICAL = historical_prompt.read()

# Temperatures
CHAT_TEMP       = 0.6
TOPIC_TEMP      = 0
HISTORICAL_TEMP = 0.2

'''Tokens'''
LONG_MEM_MAX     = 1000
RECENT_CONTEXT   = 10 # Number of messages for topic generation
N_HISTORICAL     = 5 # How many historical messages to fetch?
SHORT_MEM_MAX    = 2000

# Controls how often trim() is called.
UPPER_THRESHOLD  = 0.95
LOWER_THRESHOLD  = 0.75

CHAT_TOKEN_MAX   = 450
DISCORD_CHAR_MAX = 1500
