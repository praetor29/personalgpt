"""
memory
~~~~~~
Memory management.
"""

"""
███╗   ███╗███████╗███╗   ███╗ ██████╗ ██████╗ ██╗   ██╗
████╗ ████║██╔════╝████╗ ████║██╔═══██╗██╔══██╗╚██╗ ██╔╝
██╔████╔██║█████╗  ██╔████╔██║██║   ██║██████╔╝ ╚████╔╝ 
██║╚██╔╝██║██╔══╝  ██║╚██╔╝██║██║   ██║██╔══██╗  ╚██╔╝  
██║ ╚═╝ ██║███████╗██║ ╚═╝ ██║╚██████╔╝██║  ██║   ██║   
╚═╝     ╚═╝╚══════╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝                                                                                                     
"""

# Import libraries
import discord
import aiosqlite
from aiocache import Cache
from aiocache.serializers import PickleSerializer
import json

# Internal modules
from src.core.utility import tokenize
from src.core.constants import MEM_MAX, DB_PATH

r"""
                        .__         .__   .__                 
  ______  ____  _______ |__|_____   |  |  |__|________  ____  
 /  ___/_/ __ \ \_  __ \|  |\__  \  |  |  |  |\___   /_/ __ \ 
 \___ \ \  ___/  |  | \/|  | / __ \_|  |__|  | /    / \  ___/ 
/____  > \___  > |__|   |__|(____  /|____/|__|/_____ \ \___  >
     \/      \/                  \/                 \/     \/
"""


def serialize_message(message: discord.Message) -> str:
    data = {
        "author": (
            message.author.nick
            if hasattr(message.author, "nick")
            else message.author.name
        ),
        "channel_id": message.channel.id,
        "clean_content": message.clean_content,
        "content": message.content,
        "created_at": message.created_at.isoformat(),
        "id": message.id,
        "jump_url": message.jump_url,
    }
    return json.dumps(data)


def deserialize_message(data: str) -> dict:
    return json.loads(data)


r"""
    .___          __           ___.                            
  __| _/_____   _/  |_ _____   \_ |__  _____     ______  ____  
 / __ | \__  \  \   __\\__  \   | __ \ \__  \   /  ___/_/ __ \ 
/ /_/ |  / __ \_ |  |   / __ \_ | \_\ \ / __ \_ \___ \ \  ___/ 
\____ | (____  / |__|  (____  / |___  /(____  //____  > \___  >
     \/      \/             \/      \/      \/      \/      \/ 
"""


async def setup_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id INTEGER,
                message_id INTEGER,
                message_json TEXT,
                created_at TIMESTAMP
            )
        """
        )
        await db.commit()


async def sync_db_with_discord(bot):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT DISTINCT channel_id FROM messages")
        channels = await cursor.fetchall()

        existing_channel_ids = {channel.id for channel in bot.get_all_channels()}

        for channel in channels:
            channel_id = channel[0]
            if int(channel_id) not in existing_channel_ids:
                await db.execute(
                    "DELETE FROM messages WHERE channel_id = ?", (channel_id,)
                )
            else:
                last_message = await db.execute(
                    "SELECT message_id FROM messages WHERE channel_id = ? ORDER BY id DESC LIMIT 1",
                    (channel_id,),
                )
                last_message_id = await last_message.fetchone()

                if last_message_id:
                    last_message_id = last_message_id[0]
                    discord_channel = bot.get_channel(int(channel_id))
                    if discord_channel:
                        async for message in discord_channel.history(
                            after=discord.Object(id=last_message_id)
                        ):
                            await add_message_to_db(channel_id, message)

        await db.commit()


async def add_message_to_db(channel_id, message):
    async with aiosqlite.connect(DB_PATH) as db:
        serialized_message = serialize_message(message)
        await db.execute(
            "INSERT INTO messages (channel_id, message_id, message_json, created_at) VALUES (?, ?, ?, ?)",
            (channel_id, message.id, serialized_message, message.created_at),
        )
        await db.commit()


async def get_recent_messages_from_db(channel_id, limit=100):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT message_json FROM messages WHERE channel_id = ? ORDER BY created_at DESC LIMIT ?",
            (channel_id, limit),
        )
        rows = await cursor.fetchall()
        return [deserialize_message(row[0]) for row in rows]


r"""
                        .__             
  ____  _____     ____  |  |__    ____  
_/ ___\ \__  \  _/ ___\ |  |  \ _/ __ \ 
\  \___  / __ \_\  \___ |   Y  \\  ___/ 
 \___  >(____  / \___  >|___|  / \___  >
     \/      \/      \/      \/      \/ 
"""

cache = Cache(Cache.MEMORY, serializer=PickleSerializer())


async def populate_cache():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT DISTINCT channel_id FROM messages")
        channels = await cursor.fetchall()

        for channel in channels:
            channel_id = channel[0]
            messages = await get_recent_messages_from_db(channel_id, limit=MEM_MAX)
            token_count = 0
            cache_queue = []

            for message in messages:
                tokens = await tokenize(message["clean_content"])
                if token_count + tokens > MEM_MAX:
                    break
                cache_queue.append(message)
                token_count += tokens

            await cache.set(channel_id, cache_queue)


r"""
                                                      
  ____    ____    ______ __ __   ____   __ __   ____  
_/ __ \  /    \  / ____/|  |  \_/ __ \ |  |  \_/ __ \ 
\  ___/ |   |  \< <_|  ||  |  /\  ___/ |  |  /\  ___/ 
 \___  >|___|  / \__   ||____/  \___  >|____/  \___  >
     \/      \/     |__|            \/             \/
"""


async def enqueue(message: discord.Message):
    channel_id = str(message.channel.id)
    await add_message_to_db(channel_id, message)

    queue = await cache.get(channel_id) or []
    token_counts = [
        await tokenize(deserialize_message(msg)["clean_content"]) for msg in queue
    ]
    token_count = sum(token_counts)

    tokens = await tokenize(message.clean_content)
    if token_count + tokens <= MEM_MAX:
        queue.append(serialize_message(message))
    else:
        while token_count + tokens > MEM_MAX and queue:
            removed_message = queue.pop(0)
            token_count -= await tokenize(
                deserialize_message(removed_message)["clean_content"]
            )
        queue.append(serialize_message(message))

    await cache.set(channel_id, queue)
