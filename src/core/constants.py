"""
constants mgmt
~~~~~~~~~~~~~~
"""

"""
 ██████╗ ██████╗ ███╗   ██╗███████╗████████╗ █████╗ ███╗   ██╗████████╗███████╗
██╔════╝██╔═══██╗████╗  ██║██╔════╝╚══██╔══╝██╔══██╗████╗  ██║╚══██╔══╝██╔════╝
██║     ██║   ██║██╔██╗ ██║███████╗   ██║   ███████║██╔██╗ ██║   ██║   ███████╗
██║     ██║   ██║██║╚██╗██║╚════██║   ██║   ██╔══██║██║╚██╗██║   ██║   ╚════██║
╚██████╗╚██████╔╝██║ ╚████║███████║   ██║   ██║  ██║██║ ╚████║   ██║   ███████║
 ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝                                                                              
"""

# Import libraries
from os import path, makedirs, getenv
from dotenv import load_dotenv
import yaml
import discord

r"""
.__                   .___
|  |   _________    __| _/
|  |  /  _ \__  \  / __ | 
|  |_(  <_> ) __ \/ /_/ | 
|____/\____(____  |____ | 
                \/     \/ 
"""

# Load environment
env_path = path.join(path.dirname(__file__), "..", "..", "config", ".env")
load_dotenv(env_path)

# Load config
config_path = path.join(path.dirname(__file__), "..", "..", "config", "config.yaml")
with open(config_path, "r", encoding="utf-8") as file:
    CONFIG = yaml.safe_load(file)

# Load prompts
prompts_path = path.join(path.dirname(__file__), "..", "..", "config", "prompts.yaml")
with open(prompts_path, "r", encoding="utf-8") as file:
    PROMPTS = yaml.safe_load(file)

r"""
                     _____.__        
  ____  ____   _____/ ____\__| ____  
_/ ___\/  _ \ /    \   __\|  |/ ___\ 
\  \__(  <_> )   |  \  |  |  / /_/  >
 \___  >____/|___|  /__|  |__\___  / 
     \/           \/        /_____/  
"""

# API Keys/Tokens
OPENAI = getenv("OPENAI")
DISCORD = getenv("DISCORD")

# Dynamic IDs
BOT_ID = str()

# Bot presence
status_map = {
    "online": discord.Status.online,
    "idle": discord.Status.idle,
    "dnd": discord.Status.dnd,
    "invisible": discord.Status.invisible,
}
activity_map = {
    "playing": discord.ActivityType.playing,
    "streaming": discord.ActivityType.streaming,
    "listening": discord.ActivityType.listening,
    "watching": discord.ActivityType.watching,
}
STATUS = status_map.get(CONFIG.get("status", "dnd"))
ACTIVITY_TYPE = activity_map.get(CONFIG.get("activity").get("type", "listening"))
ACTIVITY_NAME = CONFIG.get("activity").get("name", "Waterparks")

# Memory Management
MEM_MAX = CONFIG.get("mem_max", 4096)
MEM_UPPER = CONFIG.get("threshold").get("upper", 0.90)
MEM_LOWER = CONFIG.get("threshold").get("lower", 0.75)

# OpenAI Models
CHAT_MODEL = CONFIG.get("chat").get("model", "gpt-4o")
CHAT_TEMP = CONFIG.get("chat").get("temp", 0.5)
CHAT_MAX = CONFIG.get("chat").get("tokens", 500)  # Discord has a 2000 character limit

VISION_MODEL = CONFIG.get("vision").get("model", "gpt-4o")
VISION_MAX = CONFIG.get("vision").get("max", 250)
VISION_DETAIL = CONFIG.get("vision").get("detail", "auto")

# Acceptable Media (as of present implementation)
MEDIA = {
    "image": {"png", "gif", "jpeg", "webp"},
}

r"""
                                    __          
_____________  ____   _____ _______/  |_  ______
\____ \_  __ \/  _ \ /     \\____ \   __\/  ___/
|  |_> >  | \(  <_> )  Y Y  \  |_> >  |  \___ \ 
|   __/|__|   \____/|__|_|  /   __/|__| /____  >
|__|                      \/|__|             \/ 
"""

# Chat
CHAT_PROMPT = PROMPTS.get("chat", "You are a helpful assistant.")

# Vision
VISION_PROMPT = PROMPTS.get(
    "vision",
    "Describe the image provided, for somebody who cannot see, but can understand text.",
)

r"""
    .___          __           
  __| _/_____   _/  |_ _____   
 / __ | \__  \  \   __\\__  \  
/ /_/ |  / __ \_ |  |   / __ \_
\____ | (____  / |__|  (____  /
     \/      \/             \/
"""

# Construct the path to the database file
DB_PATH = path.join(path.dirname(__file__), "..", "..", "data", "messages.db")

# Ensure the data directory exists
data_dir = path.dirname(DB_PATH)
makedirs(data_dir, exist_ok=True)
