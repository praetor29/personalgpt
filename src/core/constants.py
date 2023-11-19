'''
constants
~~~~~~~~~
Manages constants and other parameters.
'''
'''
 ██████╗ ██████╗ ███╗   ██╗███████╗████████╗ █████╗ ███╗   ██╗████████╗███████╗
██╔════╝██╔═══██╗████╗  ██║██╔════╝╚══██╔══╝██╔══██╗████╗  ██║╚══██╔══╝██╔════╝
██║     ██║   ██║██╔██╗ ██║███████╗   ██║   ███████║██╔██╗ ██║   ██║   ███████╗
██║     ██║   ██║██║╚██╗██║╚════██║   ██║   ██╔══██║██║╚██╗██║   ██║   ╚════██║
╚██████╗╚██████╔╝██║ ╚████║███████║   ██║   ██║  ██║██║ ╚████║   ██║   ███████║
 ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝                                                                              
'''

# Import libraries
from os import path, getenv
from dotenv import load_dotenv
import yaml
import discord

'''
Load
'''

# Load environment
env_path = path.join(path.dirname(__file__), '..', '..', 'config', '.env')
load_dotenv(env_path)

# Load config
config_path = path.join(path.dirname(__file__), '..', '..', 'config', 'config.yaml')
with open(config_path, "r") as file:
    CONFIG = yaml.safe_load(file)

'''
Define
'''

# API Keys/Tokens
OPENAI     = getenv('OPENAI')
DISCORD    = getenv('DISCORD')
ELEVENLABS = getenv('ELEVENLABS')

# Bot presence
status_map = {
    'online'   : discord.Status.online,
    'idle'     : discord.Status.idle,
    'dnd'      : discord.Status.dnd,
    'invisible': discord.Status.invisible,
}

activity_map = {
    'playing'  : discord.ActivityType.playing,
    'streaming': discord.ActivityType.streaming,
    'listening': discord.ActivityType.listening,
    'watching' : discord.ActivityType.watching,
}

STATUS        = status_map.get(CONFIG.get('status', 'dnd'))
ACTIVITY_TYPE = activity_map.get(CONFIG.get('activity').get('type', 'listening'))
ACTIVITY_NAME = CONFIG.get('activity').get('name', 'Waterparks')


