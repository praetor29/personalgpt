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
from src.bot import initialize, message_handler

# Configuring intents (this is crucial!!)
intents = discord.Intents.default() # default intents
intents.messages = True # add messages
intents.message_content = True # add privileged message_content (without this the bot will NOT work)

bot = discord.Bot(intents=intents)

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

@bot.event
async def on_message(message):

    if bot.user in message.mentions:
        await message_handler.response(bot=bot, message=message)
    else:
        pass # this is where we link to memory


