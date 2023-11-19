'''
bot.py
~~~~~~
Primary bot loop.
'''
'''
██████╗  ██████╗ ████████╗   ██████╗ ██╗   ██╗
██╔══██╗██╔═══██╗╚══██╔══╝   ██╔══██╗╚██╗ ██╔╝
██████╔╝██║   ██║   ██║      ██████╔╝ ╚████╔╝ 
██╔══██╗██║   ██║   ██║      ██╔═══╝   ╚██╔╝  
██████╔╝╚██████╔╝   ██║   ██╗██║        ██║   
╚═════╝  ╚═════╝    ╚═╝   ╚═╝╚═╝        ╚═╝                                                              
'''

# Import libraries
import discord
from src.core import constants

# Bot modules
from src.bot import initialize

bot = discord.Bot(
    intents=discord.Intents(messages=True)
    )

def start():
    """
    Starts the bot.
    """
    try:
        bot.run(constants.DISCORD)
    except:
        print('Unable to initialize bot.')

@bot.event
async def on_ready():
    await initialize.print_ascii()
    await initialize.set_presence(bot=bot)

