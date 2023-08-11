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
import sys
import os
from ext.fifolock import FifoLock, Read, Write
from errors.handler import handle_exception

class ShortTermMemory():
    def __init__(self, LTM: object, maxsize=0) -> None:
        '''Initialize ShortTermMemory.'''
        # Create a channel library
        self.library = {}
        # Create an intermediate cache
        self.cache   = {}
        # Create attributes
        self.maxsize = maxsize
        self.lock    = FifoLock()
        # Passthrough LongTermMemory instance
        self.LTM     = LTM
    
    '''Queue Manipulation Methods'''

    async def add(self, package: dict):
        '''Adds channel-specific package to ShortTermMemory.'''
        # Remove and allocate channel.id from package
        id = package.get('channel.id')
        # Create new entry if channel.id not in library
        async with self.lock(Write):
            if id and id not in self.library:
                self.library[id] = asyncio.Queue(maxsize=self.maxsize)
        # Enter package into specific channel.id
        await self.library[id].put(package)
        # Trim queue if required
        await self.trim(id)
    
    async def trim(self, id):
        '''
        Handles complex Queue Trimming.
        Triggers when 
        '''
        async with self.lock(Write):
            # Fetch channel specific data
            buffer_raw = self.get_raw(id) # raw packages (list)
            buffer     = self.format_snapshot(buffer_raw) # formatted snapshot list (for tokenizer)
            queue      = self.library.get(id) # actual queue

            # Run tokenizer and set upper/lower thresholds
            tokens = utility.tokenizer(input=buffer, model=constants.MODEL_CHAT)
            upper = constants.SHORT_MEM_MAX * constants.UPPER_THRESHOLD
            lower   = constants.SHORT_MEM_MAX * constants.LOWER_THRESHOLD
            if tokens > upper:
                target = lower
            else:
                target = upper

            # Sets FlushCache flag
            FlushCache = False
            
            '''Trimming Loop'''
            while tokens > target and not self.library.get(id).empty():
                # Initialize channel entry in cache
                if id not in self.cache:
                    self.cache[id] = []
                # Append oldest message to buffer and pop from queue
                self.cache[id].append(
                    await queue.get()
                    )
                FlushCache = True

                # Tokenizer Check
                trimmed = []
                trimmed.append(buffer.pop(0)) # Removes oldest message in snapshot
                tokens -= utility.tokenizer(input=trimmed,
                                            model=constants.MODEL_CHAT)
        # Flush cache if required
        if FlushCache:
            await self.flush_cache(id)
    
    async def flush_cache(self, id):
        '''
        Flushes contents of cache to LongTermMemory.
        '''
        async with self.lock(Write):
            if id in self.cache:
                try:
                    for message in self.cache[id]:
                        await self.LTM.store(message) # <--- This is where the magic happens!
                except Exception as exception:
                    print(f'Failed to flush cache.\n{handle_exception(exception)}')
                    print(f'Voiding {len(self.cache.get(id))} messages.')
            # Clean up
            if id in self.cache:
                del self.cache[id]

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
    
    async def get_raw_n(self, id, n_recent=None) -> list:
        '''
        Retrieves list of n_messages most recent raw packages from queue.
        Useful to figure out the current topic at hand.

        Links to cognition.topic()
        '''
        # If not exists, return blank []
        if id not in self.library:
            return []
        else:
            all_packages = list(self.library.get(id)._queue)
            # Return list of all packages
            if n_recent is None or n_recent > len(all_packages):
                return all_packages
            # Return list of n recent packages
            else:
                return all_packages[-n_recent:]
    
    def format_snapshot(self, buffer_raw) -> list:
        '''Formats the raw snapshot to OpenAI format.'''
        snapshot = []
        for message in buffer_raw:
            # Fetch attributes
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
                    'content' : f'{name} said:',
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
    def __init__(self):
        '''Initialize LongTermMemory.'''

    async def initialize_db(self, guild_id, channel_id):
        '''
        Initialize SQLite database for the guild (if not exist).
        Initialize new table for the channel (if not exist).
        '''
        try:
            db_path = os.path.join(constants.MEMORY_DB_PATH, f'{guild_id}.db') # Guild-specific db

            async with aiosqlite.connect(db_path) as db:
                cursor = await db.cursor()

                await cursor.execute(
                    f"""
                        CREATE TABLE IF NOT EXISTS channel_{channel_id} (
                            message_id INTEGER,
                            timestamp DATETIME,
                            author TEXT,
                            author_id INTEGER,
                            text TEXT,
                            vector TEXT
                            )
                     """)
        except Exception as exception:
            print(f'Failed to initialize table in {constants.MEMORY_DB_PATH}.\n{handle_exception(exception)}')
            print('Calling sys.exit()')
            sys.exit()

    async def store(self, message: dict):
        '''
        Store message as vector embedding in SQLite database.
        '''
        try:
            # Container metadata:
            guild_id    = message.get('guild.id')
            channel_id  = message.get('channel.id')
            message_id  = message.get('message.id')
            # Message metadata:
            timestamp   = message.get('timestamp').isoformat() # Convert to ISO 8601  format
            author_dict = message.get('author') # Container for author info           
            author      = author_dict.get('name')
            author_id   = author_dict.get('id')
            text        = message.get('message') 
            
            # Convert message content into a vector
            vector_raw  = await cognition.embed(text)
            vector      = json.dumps(vector_raw) # Serialize into json string
            
            # Initialize table in database
            await self.initialize_db(guild_id=guild_id, channel_id=channel_id)

            # Connect to SQLite database
            db_path = os.path.join(constants.MEMORY_DB_PATH, f'{guild_id}.db') # Guild-specific db
            async with aiosqlite.connect(db_path) as db:
                cursor = await db.cursor()

                await cursor.execute(
                    f"""
                        INSERT INTO channel_{channel_id} (message_id, timestamp, author, author_id, text, vector)
                        VALUES (?, ?, ?, ?, ?, ?)
                     """,
                    (message_id, timestamp, author, author_id, text, vector)
                )
                await db.commit() # Commit entry
        except Exception as exception:
            print(f'Unexpected LongTermMemory.store() error.\n{handle_exception(exception)}')
        
    async def similarity(self, topic: str):
        '''
        Fetches the top 'n' results from database.
        Based on vector cosine similarity.
        '''
        # If topic not exist, return
        if not topic:
            return
        
        # Retrieve topic vector
        topic_vector = await cognition.embed(topic)
        


'''
Vector similarity: disallow identical entries
[0.80, 1.0)

# Cache pre-existing vectors?
'''