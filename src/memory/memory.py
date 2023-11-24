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

'''
Convert Queue to List of Dicts
'''

async def unravel(message: discord.Message) -> list:
    """
    Acquire lock for safe read.
    Clone the queue into a list of dictionaries containing display_name and clean_content.
    """
    # Acquire lock
    lock = await creation.fetch_lock(message=message)

    async with lock:
        # Fetch queue
        queue = await creation.fetch_queue(message=message)

        # Note: Potentially risky accessing of internal attributes _queue
        items = list(queue._queue) # this iterates over the queue and converts it into a list

    # Create dictionaries
    construction = []
    for item in items:
        # Check if bot's message or user's
        if message.author.id == constants.BOT_ID:
            role = 'assistant'
        else:
            role = 'user'

        name_dict = {
            'role'    : 'system',
            'content' : f'{item.author.display_name} said:',
        }
        message_dict = {
            'role'    : role,
            'content' : item.clean_content,
        }

        # Add to construction list
        construction.append(name_dict)
        construction.append(message_dict)

    return construction




    
    


