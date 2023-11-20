'''
memory
~~~~~~
Memory management.
'''
'''
███╗   ███╗███████╗███╗   ███╗ ██████╗ ██████╗ ██╗   ██╗
████╗ ████║██╔════╝████╗ ████║██╔═══██╗██╔══██╗╚██╗ ██╔╝
██╔████╔██║█████╗  ██╔████╔██║██║   ██║██████╔╝ ╚████╔╝ 
██║╚██╔╝██║██╔══╝  ██║╚██╔╝██║██║   ██║██╔══██╗  ╚██╔╝  
██║ ╚═╝ ██║███████╗██║ ╚═╝ ██║╚██████╔╝██║  ██║   ██║   
╚═╝     ╚═╝╚══════╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝                                                                                                     
'''

# Import libraries
import asyncio
import discord
from src.core.utility import tokenize

# Initialize a central dict structure to hold:
# memory queues
library = {}
# token counts
counter = {}

'''
Queue Creation
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
Queueing Process
'''

async def enqueue(message: discord.message):
    """
    Fetch queue.
    Add message.
    Tokenize and increment counter.
    """
    # Fetch queue and current count
    queue   = await fetch_queue(message=message)
    tokens  = await fetch_counter(message=message)
    
    # Put message into queue
    await queue.put(message)
    
    # Update counter with new token count
    tokens += await tokenize(message.clean_content)
    counter[message.channel.id] += tokens


