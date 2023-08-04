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
            buffer = await self.read(id) # formatted snapshot (for tokenizer)
            queue  = self.library[id] # actual queue
            # Run tokenizer
            tokens = utility.tokenizer(input=buffer,
                                       model=constants.MODEL_CHAT)
            
            # Trim end of queue
            while tokens > constants.CHAT_TOKEN_MAX and not self.library[id].empty():
                await queue.get()       # Removes oldest message
                trimmed = buffer.pop(0) # Removes oldest message in snapshot
                tokens -= utility.tokenizer(input=trimmed,
                                            model=constants.MODEL_CHAT, )

    async def read(self, id) -> list:
        '''Returns contents of ShortTermMemory in role segregation.'''       
        async with self.lock(Read):
            # If not exists, return blank []
            if id not in self.library:
                return ''
            else:
                # Return list of packages
                buffer_raw = list(self.library[id]._queue)
                # Clean up and format packages
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
