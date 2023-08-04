'''
+------------------------------------------------+
 This file handles memory and context management.
+------------------------------------------------+
'''
import constants
import asyncio
import utility
from ext.fifolock import FifoLock, Read, Write

class ShortTermMemory():
    def __init__(self, maxsize=50) -> None:
        '''Initialize ShortTermMemory.'''
        # Create a channel library
        self.library = {}
        # Create attributes
        self.maxsize = maxsize
        self.lock  = FifoLock()
    
    '''Queue Manipulation Methods'''

    async def add(self, package: dict):
        '''Adds channel-specific package to ShortTermMemory.'''
        # Remove and allocate channel.id from package
        id = package.pop('channel.id')
        # Create new entry if channel.id not in library
        async with self.lock(Write):
            if id and id not in self.library:
                self.library[id] = asyncio.Queue(maxsize=self.maxsize)
        # Enter package into specific channel.id
        await self.library[id].put(package)
        # Trim queue if required
        await self.trim(id)
    
    async def trim(self, id):
        '''Trims queue to SHORT_MEM_MAX.'''
        async with self.lock(Write):
            # Fetch channel specific data
            buffer_raw = self.get_raw(id) # raw packages (list)
            buffer     = self.format_snapshot(buffer_raw) # formatted snapshot list (for tokenizer)
            queue  = self.library[id] # actual queue
            # Run tokenizer
            tokens = utility.tokenizer(input=buffer,
                                       model=constants.MODEL_CHAT)
            
            # Trim end of queue
            while tokens > constants.SHORT_MEM_MAX and not self.library[id].empty():
                await queue.get()       # Removes oldest message
                trimmed = [] # List to pass to tokenizer
                trimmed.append(buffer.pop(0)) # Removes oldest message in snapshot
                tokens -= utility.tokenizer(input=trimmed,
                                            model=constants.MODEL_CHAT, )

    async def read(self, id) -> list:
        '''Returns contents of ShortTermMemory in role segregation.'''       
        async with self.lock(Read):
             buffer_raw = self.get_raw(id) # Get raw packages
             snapshot   = self.format_snapshot(buffer_raw)
             return snapshot
    
    '''Data Processing Methods'''
    def get_raw(self, id) -> list:
        '''Retrieves list of raw packages from queue.'''
        # If not exists, return blank []
        if id not in self.library:
            return []
        else:
            # Return list of packages
            return list(self.library[id]._queue)
    
    def format_snapshot(self, buffer_raw) -> list:
        '''Formats the raw snapshot to OpenAI format.'''
        snapshot = []
        for message in buffer_raw:
            # Fetch attributes
            timestamp = message.get('timestamp')
            name      = message.get('author').get('name')
            text      = message.get('message') 
            # Designate role
            author_id = message.get('author').get('id')
            if str(author_id) == str(constants.DISCORD_BOT_ID):
                role  = 'assistant'
            else:
                role  = 'user'
            # Format
            snapshot.append(
                {
                'role'    : 'system',
                'content' : f'{timestamp} | {name}:',
                }
            )
            snapshot.append(
                {
                'role'    : role,
                'content' : text,
                }
            )
        # Return conversation list
        return snapshot
