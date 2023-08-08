'''
+------------------------------------------------+
 This file handles memory and context management.
+------------------------------------------------+
'''
import constants
import cognition
import asyncio
import utility
import aiosqlite
import json
from ext.fifolock import FifoLock, Read, Write
from errors.handler import handle_exception

class ShortTermMemory():
    def __init__(self, maxsize=0) -> None:
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
            queue  = self.library.get(id) # actual queue
            # Run tokenizer
            tokens = utility.tokenizer(input=buffer,
                                       model=constants.MODEL_CHAT)
            
            # Trim end of queue
            while tokens > constants.SHORT_MEM_MAX and not self.library.get(id).empty():
                await queue.get()       # Removes oldest message
                trimmed = [] # List to pass to tokenizer
                trimmed.append(buffer.pop(0)) # Removes oldest message in snapshot
                tokens -= utility.tokenizer(input=trimmed,
                                            model=constants.MODEL_CHAT, )

    async def read(self, id) -> list:
        '''Returns contents of ShortTermMemory with role segregation.'''       
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
            return list(self.library.get(id)._queue)
    
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

class LongTermMemory():
    async def __init__(self, db_path: str):
        '''Initialize LongTermMemory.'''
        self.db_path = db_path

        # Initialize memory table in SQLite database
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.cursor()

            await cursor.execute(
                """
                    CREATE TABLE IF NOT EXISTS memory (
                        key INTEGER PRIMARY KEY,
                        id INTEGER,
                        timestamp DATETIME,
                        name TEXT,
                        text TEXT,
                        vector TEXT
                        )
                """)

    async def store(self, message: dict):
        '''Store message as vector embedding in SQLite database.'''
        try:
            # Retrieve message metadata
            id        = message.get('channel.id')
            timestamp = utility.sql_date( # Convert to SQL format
                        message.get('timestamp')
                        )
            name      = message.get('author').get('name')
            text      = message.get('message') 

            # Convert message content into a vector
            vector      = await cognition.embed(text)
            vector_json = json.dumps(vector) # Serialize into json string

            # Connect to SQLite database
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.cursor()

                await cursor.execute(
                    """
                        INSERT INTO memory (id, timestamp, name, text, vector)
                        VALUES (?, ?, ?, ?, ?)
                    """,
                    (id, timestamp, name, text, vector_json)
                )
        except Exception as exception:
            print(f'Unexpected LongTermMemory.store() error.\n{handle_exception(exception)}')

'''
Vector similarity: disallow identical entries
[0.80, 1.0)
'''