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
from discord.ext.commands import Bot
import sys

# Internal modules
from src.core import constants, ascii
from src.core.utility import clear
from src.bot.memory import sync_cache, setup_memory, enqueue, cache

# Bot permissions
intents = discord.Intents.default()  # default intents
intents.message_content = True  # read messages

# Create bot client instance
bot = Bot(command_prefix=None, intents=intents)


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
    await bot.tree.sync()  # TODO: re-enable

    print("Syncing memory with discord.")
    await setup_memory(bot)

    # clear()
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
Maintenance
"""


@bot.event
async def on_guild_join(guild):
    """
    Handle event when the bot joins a new guild.
    """
    for channel in guild.text_channels:
        await sync_cache(channel)


@bot.event
async def on_guild_channel_create(channel):
    """
    Handle event when a new channel is created in a guild.
    """
    await sync_cache(channel)


"""
/Slash Commands
"""


@bot.tree.command(name="ping", description="Check latency.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"`{round(bot.latency * 1000, 3)}` ms.", ephemeral=True
    )


@bot.tree.command(name="cached", description="Show cached messages.")
async def show_cache(interaction: discord.Interaction):
    channel_id = str(interaction.channel_id)
    recent_messages = await cache.get(channel_id) or []

    if recent_messages:
        messages_text = "\n".join([msg.clean_content for msg in recent_messages])
        await interaction.response.send_message(messages_text[:2000], ephemeral=True)
    else:
        await interaction.response.send_message(
            "No messages are cached.", ephemeral=True
        )
