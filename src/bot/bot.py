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
from src.voice.voice import Voice

# Configuring intents (this is crucial!!)
intents = discord.Intents.default() # default intents
intents.messages = True # add messages
intents.message_content = True # add privileged message_content (without this the bot will NOT work)

bot = discord.Bot(intents=intents)

def start():
    """
    Adds any cogs and starts the bot.
    """
    try:
        # Add cogs
        bot.add_cog(Voice(bot)) # Voice functionality

        # Start bot proper
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

    # Set discord presence
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

'''
/Slash Commands
'''
@bot.slash_command(description="Check latency.")
async def ping(ctx):
    await ctx.respond(f"`{round(bot.latency, 3)}` ms.", ephemeral=True)

#######################################################################

'''
THINGS TO WORK ON IN THIS REFACTORING:

1. All other features like read() need VC command to be active, and add onto vc()

'''