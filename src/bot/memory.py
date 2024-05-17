"""
memory
~~~~~~
Memory management.
"""

"""
███╗   ███╗███████╗███╗   ███╗ ██████╗ ██████╗ ██╗   ██╗
████╗ ████║██╔════╝████╗ ████║██╔═══██╗██╔══██╗╚██╗ ██╔╝
██╔████╔██║█████╗  ██╔████╔██║██║   ██║██████╔╝ ╚████╔╝ 
██║╚██╔╝██║██╔══╝  ██║╚██╔╝██║██║   ██║██╔══██╗  ╚██╔╝  
██║ ╚═╝ ██║███████╗██║ ╚═╝ ██║╚██████╔╝██║  ██║   ██║   
╚═╝     ╚═╝╚══════╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝                                                                                                     
"""

# Import libraries
import discord
from aiocache import SimpleMemoryCache

# Internal modules
from src.core.utility import tokenize
from src.core.constants import MEM_MAX

r"""
                        .__             
  ____  _____     ____  |  |__    ____  
_/ ___\ \__  \  _/ ___\ |  |  \ _/ __ \ 
\  \___  / __ \_\  \___ |   Y  \\  ___/ 
 \___  >(____  / \___  >|___|  / \___  >
     \/      \/      \/      \/      \/ 
"""

cache = SimpleMemoryCache(serializer=None)


async def setup_memory(bot):
    """
    Setup memory for all channels in all guilds the bot is in, and all existing DMs.
    """
    for guild in bot.guilds:
        print(f"Setting up memory for guild {guild.name}")
        for channel in guild.text_channels:
            print(f"Setting up memory for channel {channel.name}")
            await sync_cache(channel)

async def fetch_channel_history(channel, limit=100):
    """
    Fetch message history of a text-based channel in batches.
    """
    messages = []
    try:
        if isinstance(channel, (discord.TextChannel, discord.DMChannel)):
            async for message in channel.history(limit=limit, oldest_first=False):
                messages.append(message)
    except Exception as e:
        print(f"Error fetching history for channel {channel.id}: {e}")
    return messages


async def sync_cache(channel, max_iterations=4, batch_size=25):
    """
    Populate the cache for a given channel with messages until MEM_MAX tokens are reached.
    """
    if isinstance(channel, (discord.TextChannel, discord.DMChannel)):
        token_count = 0
        cache_queue = []
        iterations = 0

        while token_count < MEM_MAX and iterations < max_iterations:
            messages = await fetch_channel_history(channel, limit=batch_size)
            if not messages:
                break  # No more messages to fetch

            for message in messages:
                tokens = await tokenize(message.clean_content)
                if token_count + tokens > MEM_MAX:
                    break
                cache_queue.append(message)
                token_count += tokens

            iterations += 1

            if token_count >= MEM_MAX or len(messages) < batch_size:
                break  # Reached token limit or no more messages to fetch

        await cache.set(str(channel.id), cache_queue)


r"""
                                                      
  ____    ____    ______ __ __   ____   __ __   ____  
_/ __ \  /    \  / ____/|  |  \_/ __ \ |  |  \_/ __ \ 
\  ___/ |   |  \< <_|  ||  |  /\  ___/ |  |  /\  ___/ 
 \___  >|___|  / \__   ||____/  \___  >|____/  \___  >
     \/      \/     |__|            \/             \/
"""


async def enqueue(message: discord.Message):
    """
    Add a new message to the cache, trimming the queue if the token limit is exceeded.
    """
    channel_id = str(message.channel.id)

    queue = await cache.get(channel_id) or []
    token_counts = [await tokenize(msg.clean_content) for msg in queue]
    token_count = sum(token_counts)

    tokens = await tokenize(message.clean_content)
    if token_count + tokens <= MEM_MAX:
        queue.append(message)
    else:
        while token_count + tokens > MEM_MAX and queue:
            removed_message = queue.pop(0)
            token_count -= await tokenize(removed_message.clean_content)
        queue.append(message)

    await cache.set(channel_id, queue)
