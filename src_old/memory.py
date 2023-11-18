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
import annoy
import json
import sys
import os
from datetime import datetime
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
            # SQL database
            db_path = os.path.join(constants.MEMORY_DB_PATH, f'{guild_id}.db') # Guild-specific db
            query   = f"""
                        CREATE TABLE IF NOT EXISTS channel_{channel_id} (
                            key INTEGER PRIMARY KEY,
                            message_id INTEGER,
                            timestamp DATETIME,
                            author TEXT,
                            author_id INTEGER,
                            text TEXT,
                            vector TEXT
                            )
                     """
            async with aiosqlite.connect(db_path) as db:
                cursor = await db.cursor()
                await cursor.execute(query)
            
            # Annoy Index
            index_path = os.path.join(constants.MEMORY_VECTOR_PATH, f'{guild_id}')
            os.makedirs(index_path, exist_ok=True)
            
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
            query   = f"""
                        INSERT INTO channel_{channel_id} (message_id, timestamp, author, author_id, text, vector)
                        VALUES (?, ?, ?, ?, ?, ?)
                     """
            async with aiosqlite.connect(db_path) as db:
                cursor = await db.cursor()
                await cursor.execute(
                    query, (message_id, timestamp, author, author_id, text, vector)
                )
                await db.commit() # Commit entry

            '''
            Mirror newly stored message into Annoy database
            '''   
            try:
                await self.indexing(guild_id=guild_id, channel_id=channel_id)
            except Exception as exception:
                print(f'Unexpected LongTermMemory.store() error.\n{handle_exception(exception)}')

        except Exception as exception:
            print(f'Unexpected LongTermMemory.store() error.\n{handle_exception(exception)}')
    
    async def indexing(self, guild_id: int, channel_id: int):
        '''
        Builds the Spotify Annoy Index for each channel of each server.
        [Annoy](https://github.com/spotify/annoy)

        Adds each item from SQLite db to the index.
        '''
        try:
            # Defines the index
            index = annoy.AnnoyIndex(constants.VECTOR_LENGTH, 'angular')
            
            # SQLite information
            db_path = os.path.join(constants.MEMORY_DB_PATH, f'{guild_id}.db') # Guild-specific db
            table   = f'channel_{channel_id}'
            query   = f"SELECT key, vector FROM {table}"

            async with aiosqlite.connect(db_path) as db:
                cursor = await db.execute(query) # Select all rows
                async for row in cursor:
                    key, vector_json = row # Fetch info from each row
                    vector = json.loads(vector_json) # Convert from json-string to raw floats
                    if vector:
                        index.add_item(key, vector=vector) # Add to index
                    else:
                        return
            
            index.build(constants.ANNOY_TREES) # Build index
            
            index_path = os.path.join(constants.MEMORY_VECTOR_PATH, f'{guild_id}', f'{channel_id}.annoy')
            index.save(index_path) # Saves index to disk

        except Exception as exception:
            print(f'Unexpected LongTermMemory.indexing() error.\n{handle_exception(exception)}')
        
    async def similarity(self, topic: str, guild_id: int, channel_id: int) -> list:
        '''
        Fetches the top 'n' nearest neighbor results from database.
        Uses the Spotify Annoy algorithm.

        Returns a list of SQL PRIMARY INTEGER KEY values.
        '''
        # If recent topic not exist, return
        if not topic:
            return
        
        # Retrieve topic vector
        topic_vector = await cognition.embed(topic)
        
        # Define index
        index = annoy.AnnoyIndex(constants.VECTOR_LENGTH, 'angular')
        index_path = os.path.join(constants.MEMORY_VECTOR_PATH, f'{guild_id}', f'{channel_id}.annoy')
        if not os.path.exists(index_path):
            return
        
        # Loads specified index
        index.load(index_path) # Retrieves index from list
        
        # Fetch results
        indices, _ = index.get_nns_by_vector(topic_vector, constants.N_HISTORICAL, include_distances=True)
        return indices
    
    async def similarity_SQL(self, indices: list, guild_id: int, channel_id: int) -> list:
        '''
        Return the list of messages corresponsing to the indices provided.
        '''
        try:
            # If indices is empty, return
            if not indices:
                return []
            
            # Convert indices to comma-separated string
            keys = ','.join(map(str, indices))

            # SQLite information
            db_path = os.path.join(constants.MEMORY_DB_PATH, f'{guild_id}.db') # Guild-specific db
            table   = f'channel_{channel_id}'
            query   = f"""
                        SELECT key, timestamp, author, text 
                        FROM {table} 
                        WHERE key IN ({keys})
                    """

            # Initialize a list to store the result
            result = []

            async with aiosqlite.connect(db_path) as db:
                cursor = await db.execute(query) # Select specified rows

                async for row in cursor:
                    key, timestamp_str, author, text = row # Fetch info from each row
                    
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str)
                    except Exception:
                        timestamp = ''

                    package = {
                        'timestamp': timestamp,
                        'author'   : author,
                        'text'     : text
                    }

                    result.append(package) # Add package dict to list
            return result
        except Exception as exception:
            print(f'Failed to fetch data from {db_path}.\n{handle_exception(exception)}')
            return [] # Return an empty list

'''
Vector similarity: disallow identical entries
[0.80, 1.0)

# Cache pre-existing vectors?
'''