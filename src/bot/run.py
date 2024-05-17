"""
core bot loop
~~~~~~~~~~~~~
"""

"""
██████╗  ██████╗ ████████╗   ██████╗ ██╗   ██╗
██╔══██╗██╔═══██╗╚══██╔══╝   ██╔══██╗╚██╗ ██╔╝
██████╔╝██║   ██║   ██║      ██████╔╝ ╚████╔╝ 
██╔══██╗██║   ██║   ██║      ██╔═══╝   ╚██╔╝  
██████╔╝╚██████╔╝   ██║   ██╗██║        ██║   
╚═════╝  ╚═════╝    ╚═╝   ╚═╝╚═╝        ╚═╝                                                              
"""

# Import libraries
import discord
import sys

# Internal modules
from src.core import constants, ascii
from src.core.utility import clear
from src.bot.memory import (
    setup_db,
    sync_db_with_discord,
    populate_cache,
    enqueue,
    cache,  # aiocache object
    deserialize_message,
)

# Bot permissions
intents = discord.Intents.default()  # default intents
intents.message_content = True  # read messages

# Create bot client instance
bot = discord.Client(intents=intents)
# Register slash commands
tree = discord.app_commands.CommandTree(bot)


def start():
    """
    Starts the bot.
    """
    clear()

    try:
        # Start bot proper
        bot.run(constants.DISCORD)

    except Exception as e:
        print(f"Unable to initialize bot: {e}")
        sys.exit(f"Unable to initialize bot: {e}")


@bot.event
async def on_ready():
    """
    Run initialization functions.
    """
    print("Logged into discord.")

    # Add Bot user ID to constants
    constants.BOT_ID = bot.user.id

    # Set discord presence
    await bot.change_presence(
        status=constants.STATUS,
        activity=discord.Activity(
            type=constants.ACTIVITY_TYPE,
            name=constants.ACTIVITY_NAME,
        ),
    )
    print("Set bot presence.")

    # Sync commands
    print("Syncing commands.")
    await tree.sync()

    # Load memory
    print("Setting up database.")
    await setup_db()

    print("Syncing database with discord.")
    await sync_db_with_discord(bot)

    print("Populating cache.")
    await populate_cache()

    clear()
    print(ascii.personalgpt)


@bot.event
async def on_message(message):
    """
    Memory functionality upon receiving a new message.
    """
    # Message handling
    await enqueue(message=message)

    # Reply if mentioned
    if bot.user in message.mentions:

        await message.reply("Message received.")

        # # Divert message through media handler if it contains attachments
        # if message.attachments:
        #     # Verify attachments
        #     media = await media_handler.verify_media(message=message)

        #     # If list of verified exists, proceed.
        #     if media:
        #         await media_handler.reply_media(message=message, media=media)
        #     else:
        #         await message_handler.reply(message=message)
        # else:
        #     await message_handler.reply(message=message)


"""
/Slash Commands
"""


@tree.command(name="ping", description="Check latency.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"`{round(bot.latency, 3)}` ms.", ephemeral=True
    )


@tree.command(name="cached", description="Show cached messages.")
async def show_cache(interaction: discord.Interaction):
    channel_id = str(interaction.channel_id)
    recent_messages = await cache.get(channel_id) or []
    messages_text = "\n".join(
        [deserialize_message(msg)["clean_content"] for msg in recent_messages]
    )
    await interaction.response.send_message(f"Cached messages:\n{messages_text}")
