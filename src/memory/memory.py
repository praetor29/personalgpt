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
            print(await creation.fetch_trim(message=message))
            print('trim activated')
            await trim(message=message)

    
async def encount(message: discord.message):
    """
    Tokenize and increment counter.
    """
    # Fetch token count
    tokens  = await creation.fetch_counter(message=message)

    # Tokenize message
    tokens += await tokenize(message.clean_content)

    # Update counter with new token count
    creation.counter[message.channel.id] += tokens
    

'''
Trimming Process
'''

# async def trim(message: discord.message):
#     """
#     Trim the queue from upper threshold to lower threshold (hysteresis).

#     (https://en.wikipedia.org/wiki/Hysteresis#Control_systems)
#     """

#     # Fetch queue
#     queue   = await creation.fetch_queue(message=message)

#     # Begin trim loop
#     while creation.counter[message.channel.id] > (constants.MEM_MAX * constants.MEM_LOWER): # trim to lower threshold
#         # Remove message object from beginning of queue (FIFO)
#         takeout = await queue.get()

#         # Tokenize removed message (takeout)
#         tokens  = await tokenize(takeout.clean_content)
        
#         # Decrement token counter
#         creation.counter[message.channel.id] -= tokens

#         # Declare .get() operation as done
#         queue.task_done()

async def trim(message: discord.message):
    """
    Trim the queue from upper threshold to lower threshold (hysteresis).

    (https://en.wikipedia.org/wiki/Hysteresis#Control_systems)
    """
    print('Trim process initiated.')

    # Fetch queue
    print('Fetching queue...')
    queue = await creation.fetch_queue(message=message)
    print('Queue fetched.')

    # Check initial token count
    initial_tokens = creation.counter[message.channel.id]
    print(f'Initial token count: {initial_tokens}')

    # Begin trim loop
    while creation.counter[message.channel.id] > (constants.MEM_MAX * constants.MEM_LOWER):
        print('Trim loop iteration started.')

        # Check if queue is empty
        if queue.empty():
            print('Queue is empty. Breaking out of trim loop.')
            break

        # Remove message object from beginning of queue (FIFO)
        print('Retrieving message from queue...')
        takeout = await queue.get()
        print('Message retrieved from queue.')

        # Tokenize removed message (takeout)
        print('Tokenizing message...')
        tokens = await tokenize(takeout.clean_content)
        print(f'Tokenized. Tokens in message: {tokens}')

        # Decrement token counter
        creation.counter[message.channel.id] -= tokens
        print(f'Tokens after decrement: {creation.counter[message.channel.id]}')

        # Declare .get() operation as done
        queue.task_done()
        print('Queue task marked as done.')

    print('Trim process completed.')
    print(f'Final token count: {creation.counter[message.channel.id]}')
    print(f'Tokens reduced by: {initial_tokens - creation.counter[message.channel.id]}')
