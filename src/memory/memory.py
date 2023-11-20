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
import discord
from src.memory import creation
from src.core import constants
from src.core.utility import tokenize

'''
Queueing Process
'''

async def enqueue(message: discord.message):
    """
    Acquire channel lock.

    Fetch queue.
    Add message.
    Call encount.
    """
    # Acquire lock
    lock = await creation.fetch_lock(message=message)

    async with lock:
        # Fetch queue
        queue   = await creation.fetch_queue(message=message)
        
        # Put message into queue
        await queue.put(message)

        # Call encount
        await encount(message=message)

        # Begin trim if required
        if await creation.fetch_trim(message=message):
            await trim(message=message)

    
async def encount(message: discord.message):
    """
    Tokenize and increment counter.
    """
    # Fetch current token count
    current_tokens  = await creation.fetch_counter(message=message)

    # Tokenize message
    new_tokens = await tokenize(message.clean_content)
    
    # Update counter with updated token count
    creation.counter[message.channel.id] = current_tokens + new_tokens
    

'''
Trimming Process
'''

async def trim(message: discord.message):
    """
    Trim the queue from upper threshold to lower threshold (hysteresis).

    (https://en.wikipedia.org/wiki/Hysteresis#Control_systems)
    """
    # Fetch queue
    queue   = await creation.fetch_queue(message=message)

    # Begin trim loop
    while creation.counter[message.channel.id] > (constants.MEM_MAX * constants.MEM_LOWER): # trim to lower threshold
        # Remove message object from beginning of queue (FIFO)
        takeout = await queue.get()

        # Tokenize removed message (takeout)
        tokens  = await tokenize(takeout.clean_content)
        
        # Decrement token counter
        creation.counter[message.channel.id] -= tokens

        # Declare .get() operation as done
        queue.task_done()
