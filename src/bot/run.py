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
from datetime import datetime
import sys

# Internal modules
from src.core import constants, ascii
from src.core.utility import clear, get_channel_name
from src.cognition.memory import sync_cache, setup_memory, enqueue, cache
from src.bot.neuron import reply, send

r"""
.__         .__   __   .__         .__   .__                 
|__|  ____  |__|_/  |_ |__|_____   |  |  |__|________  ____  
|  | /    \ |  |\   __\|  |\__  \  |  |  |  |\___   /_/ __ \ 
|  ||   |  \|  | |  |  |  | / __ \_|  |__|  | /    / \  ___/ 
|__||___|  /|__| |__|  |__|(____  /|____/|__|/_____ \ \___  >
         \/                     \/                 \/     \/ 
"""

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
    clear()
    print(ascii.personalgpt)
    print(ascii.dash)

    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("Authorization successful. ✅")

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
    print("Established construct persona link. ✅")

    # Sync commands
    print("Engaging cyberdeck commands. ✅")
    await bot.tree.sync()

    print(ascii.dash)
    print("SYNCING CONSTRUCT WITH DISCORD. 🔄")
    await setup_memory(bot)
    print("MEMORY AT 100%. CONSTRUCT ONLINE. 🌐")
    print(ascii.dash)
    print("System log:")


r"""
                                                          
  _____    ____    ______  ___________      ____    ____  
 /     \ _/ __ \  /  ___/ /  ___/\__  \    / ___\ _/ __ \ 
|  Y Y  \\  ___/  \___ \  \___ \  / __ \_ / /_/  >\  ___/ 
|__|_|  / \___  >/____  >/____  >(____  / \___  /  \___  >
      \/      \/      \/      \/      \/ /_____/       \/ 
"""


@bot.event
async def on_message(message):
    """
    Memory functionality upon receiving a new message.
    """
    # Re-sync cache if doesn't exist
    if await cache.get(message.channel.id) is None:
        await sync_cache(message.channel)

    # Message handling
    await enqueue(message=message)

    # Ignore bot messages
    if message.author == bot.user:
        return

    # Different behavior in DMs and Guilds
    if bot.user in message.mentions:
        await reply(message)
    elif isinstance(message.channel, discord.DMChannel):
        await send(message)


r"""
     /\         .__                   .__     
    / /   ______|  |  _____     ______|  |__  
   / /   /  ___/|  |  \__  \   /  ___/|  |  \ 
  / /    \___ \ |  |__ / __ \_ \___ \ |   Y  \
 / /    /____  >|____/(____  //____  >|___|  /
 \/          \/            \/      \/      \/ 
"""


@bot.tree.command(name="ping", description="Check latency.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"`{round(bot.latency * 1000, 3)}` ms.", ephemeral=True
    )


@bot.tree.command(name="re-cache", description="Recache messages in channel.")
async def reset_cache(interaction: discord.Interaction):
    channel_name = get_channel_name(interaction.channel)
    try:
        await sync_cache(interaction.channel)
        await interaction.response.send_message(
            f"`#{channel_name}` messages succesfully re-cached.",
            ephemeral=True,
        )
    except Exception as e:
        await interaction.response.send_message(
            f"Error re-caching `#{channel_name}` messages: {e}",
            ephemeral=True,
        )
