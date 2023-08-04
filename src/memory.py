'''
+------------------------------------------------+
 This file handles memory and context management.
+------------------------------------------------+
'''

import constants
import asyncio
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
    
    async def read(self, id) -> list:
        '''Fetches list of packages in ShortTermMemory.'''       
        async with self.lock(Read):
            # If not exists, return blank []
            if id not in self.library:
                return []
            else:
                # Return list of packages
                return list(self.library[id]._queue)
