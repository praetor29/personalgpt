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
.__                   .___
|  |   _________    __| _/
|  |  /  _ \__  \  / __ | 
|  |_(  <_> ) __ \/ /_/ | 
|____/\____(____  |____ | 
                \/     \/ 
'''

# Load environment
env_path = path.join(path.dirname(__file__), '..', '..', 'config', '.env')
load_dotenv(env_path)

# Load config
config_path = path.join(path.dirname(__file__), '..', '..', 'config', 'config.yaml')
with open(config_path, 'r', encoding='utf-8') as file:
    CONFIG = yaml.safe_load(file)

# Load prompts
prompts_path = path.join(path.dirname(__file__), '..', '..', 'config', 'prompts.yaml')
with open(prompts_path, 'r', encoding='utf-8') as file:
    PROMPTS = yaml.safe_load(file)

'''
                     _____.__        
  ____  ____   _____/ ____\__| ____  
_/ ___\/  _ \ /    \   __\|  |/ ___\ 
\  \__(  <_> )   |  \  |  |  / /_/  >
 \___  >____/|___|  /__|  |__\___  / 
     \/           \/        /_____/  
'''

# API Keys/Tokens
OPENAI            = getenv('OPENAI')
DISCORD           = getenv('DISCORD')
ELEVENLABS        = getenv('ELEVENLABS')

# Dynamic IDs
BOT_ID = str()

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

# Memory Management
MEM_MAX   = CONFIG.get('mem_max', 4096)
MEM_UPPER = CONFIG.get('threshold').get('upper', 0.95)
MEM_LOWER = CONFIG.get('threshold').get('lower', 0.75)

# OpenAI Models
CHAT_MODEL = CONFIG.get('chat').get('model', 'gpt-3.5-turbo')
CHAT_TEMP  = CONFIG.get('chat').get('temp', 0.6)
CHAT_MAX   = CONFIG.get('chat').get('tokens', 512)

VISION_MODEL  = CONFIG.get('vision').get('model', 'gpt-4-vision-preview')
VISION_MAX    = CONFIG.get('vision').get('max', 250)
VISION_DETAIL = CONFIG.get('vision').get('detail', 'auto')

WHISPER_MODEL = CONFIG.get('whisper').get('model', 'whisper-1')
WHISPER_LANG  = CONFIG.get('whisper').get('lang', None)

# ElevenLabs
VOICE_ID         = CONFIG.get('voice').get('id')
VOICE_STABILITY  = CONFIG.get('voice').get('stability')
VOICE_SIMILARITY = CONFIG.get('voice').get('similarity')
VOICE_STYLE      = CONFIG.get('voice').get('style')
VOICE_BOOST      = CONFIG.get('voice').get('boost', True)
VOICE_MODEL      = CONFIG.get('voice').get('model', 'eleven_turbo_v2')

# Acceptable Media (as of present implementation)
MEDIA = {
    'image' : {'png', 'gif', 'jpeg', 'webp'},
}

# Voice Acitvity Detection (VAD)
VAD_MODE           = CONFIG.get('mode', 3)
VAD_FRAME_DURATION = CONFIG.get('duration', 30)
VAD_SMOOTHING      = CONFIG.get('smoothing', 3)

# Voice Channel
VOICE_IDLE = CONFIG.get('idle', 60)

'''
                                    __          
_____________  ____   _____ _______/  |_  ______
\____ \_  __ \/  _ \ /     \\____ \   __\/  ___/
|  |_> >  | \(  <_> )  Y Y  \  |_> >  |  \___ \ 
|   __/|__|   \____/|__|_|  /   __/|__| /____  >
|__|                      \/|__|             \/ 
'''

# Chat
CHAT_PROMPT   = PROMPTS.get('chat', 'Ask the user to set a prompt under `config/prompts.yaml`.')

# Vision
VISION_PROMPT  = PROMPTS.get('vision', 'Describe the image provided, for somebody who cannot see, but can understand text.')

# Whisper
WHISPER_PROMPT = PROMPTS.get('whisper', None)