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
from src.bot import initialize, message_handler, media_handler
from src.core import constants
from src.memory import memory
from src.voice import voice

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
    # Add Bot user ID to constants
    constants.BOT_ID = bot.user.id

    await initialize.set_presence(bot=bot)

    # Print ASCII in terminal to signify ready
    await initialize.print_ascii()

@bot.event
async def on_message(message):
    '''
    Memory functionality upon receiving a new message.
    '''
    # Enqueue message
    await memory.enqueue(message=message)
    
    # Reply if mentioned
    if bot.user in message.mentions:

        # Divert message through media handler if it contains attachments
        if message.attachments:
            # Verify attachments
            media = await media_handler.verify_media(message=message)

            # If list of verified exists, proceed.
            if media:
                await media_handler.reply_media(message=message, media=media)
            else:
                await message_handler.reply(message=message)
        else:
            await message_handler.reply(message=message)

@bot.slash_command(name="speak")
async def speak(ctx):
    await voice.speak(ctx=ctx)

