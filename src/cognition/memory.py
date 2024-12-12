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
import asyncio
from aiocache import SimpleMemoryCache

# Internal modules
from src.core.utility import tokenize, get_channel_name
from src.core.constants import MEM_MAX, MEM_SYNC

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
    tasks = []

    for guild in bot.guilds:
        print(f"Setting up memory for guild {guild.name}")
        for channel in guild.text_channels:
            tasks.append(sync_cache(channel))

    await asyncio.gather(*tasks)


async def sync_cache(channel):
    """
    Fetch and tokenize messages from the channel one at a time until MEM_MAX tokens are reached.
    Store messages in cache in reverse order (chronologically earliest message first).
    """
    if isinstance(channel, (discord.TextChannel, discord.Thread, discord.DMChannel)):
        token_count = 0
        cache_queue = []

        channel_name = get_channel_name(channel)

        try:
            async for message in channel.history(limit=None, oldest_first=False):
                if message.clean_content and not message.flags.ephemeral:
                    tokens = await tokenize(message.clean_content)
                    if token_count + tokens > (MEM_MAX * MEM_SYNC):
                        break
                    cache_queue.append(message)
                    token_count += tokens
        except Exception as e:
            print(f"Sync error for #{channel_name}: {e}")

        # Reverse the order of messages before caching
        cache_queue.reverse()
        await cache.set(channel.id, cache_queue)


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
    channel_id = message.channel.id

    queue = await cache.get(channel_id) or []
    token_counts = [await tokenize(msg.clean_content) for msg in queue]
    token_count = sum(token_counts)

    tokens = await tokenize(message.clean_content)
    if token_count + tokens <= MEM_MAX and not message.flags.ephemeral:
        queue.append(message)
    else:
        while token_count + tokens > MEM_MAX and queue:
            removed_message = queue.pop(0)
            token_count -= await tokenize(removed_message.clean_content)
        queue.append(message)

    await cache.set(channel_id, queue)
