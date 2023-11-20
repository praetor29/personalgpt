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

# Internal modules
from src.bot import initialize, message_handler
from src.core import constants, utility
from src.memory import memory, creation

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
    '''
    Run ititialization functions.
    '''
    await initialize.print_ascii()
    await initialize.set_presence(bot=bot)

@bot.event
async def on_message(message):
    '''
    Memory functionality upon receiving a new message.
    '''
        # await message_handler.response(bot=bot, message=message)
    
    await memory.enqueue(message=message)
    print(await creation.fetch_counter(message=message))


    


