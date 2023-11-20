'''
Create data structures.
~~~~~~~~~~~~~~~~~~~~~~~
'''

# Import libraries
import asyncio
import discord

from src.core import constants

# Initialize central dict structures to hold:
## memory queues
library = {}
## token counts
counter = {}
## channel locks (for thread safety)
locker   = {}

'''
Queue/Counter Creation
'''

async def fetch_queue(message: discord.message) -> asyncio.Queue:
    """
    Fetch status of message channel's queue in library.

    If exists -> return queue.
    Else -> create and return queue.
    """

    if message.channel.id not in library:
        library[message.channel.id] = asyncio.Queue() 
    
    return library[message.channel.id]

async def fetch_counter(message: discord.message) -> int:
    """
    Fetch status of message channel's token counter.

    If exists -> return count.
    Else -> create counter and return count.
    """

    if message.channel.id not in counter:
        counter[message.channel.id] = 0  
    
    return counter[message.channel.id]

'''
Lock Creation
'''
async def fetch_lock(message: discord.message) -> asyncio.Lock:
    """
    Fetch status of channel lock.
    If not locked, locks and returns lock.
    """
    if message.channel.id not in locker:
        locker[message.channel.id] = asyncio.Lock()
    return locker[message.channel.id]

'''
Trim Check
'''

async def fetch_trim(message: discord.message) -> bool:
    """
    Check if trim is required. Returns bool.
    """
    return counter[message.channel.id] > (constants.MEM_MAX * constants.MEM_UPPER)



