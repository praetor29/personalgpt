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

# @bot.event
# async def on_voice_state_update(member, before, after):
#     """
#     Disconnect handler.
#     """
#     # Check if the bot is the member and has left a voice channel
#     if member == bot.user and after.channel is None:
#         guild_id = member.guild.id  # Access guild ID through the member object
#         # Check if the guild is in the voice connections and remove it if present
#         voice.connections.pop(guild_id, None)

'''
/Slash Commands
'''
@bot.slash_command(description="Check latency.")
async def ping(ctx):
    await ctx.respond(f"`{round(bot.latency, 3)}` ms.", ephemeral=True)

@bot.slash_command(description='Read text aloud.')
async def read(ctx, text: str):
    # Ensure it's in a guild
    if ctx.guild is None:
        await ctx.respond(f"i can only vc in servers", ephemeral=True)
        return

    # Create/retrieve voice client
    voice_client = await voice.connect(ctx=ctx)

    if not voice_client or not voice_client.is_connected():
        await ctx.respond(f"i think it broke", ephemeral=True)
        voice.connections.pop(ctx.guild.id, None)
        return
    
    # Respond ephemerally with text to be read in quotes.
    await ctx.respond(f'> “{text}”', ephemeral=True)

    # Begin read()
    await voice.read(ctx=ctx, voice_client=voice_client, text=text)

    # Handover to alone() if required
    if (
        not voice.connections.get(ctx.guild.id, {}).get('state') and
        not voice.connections.get(ctx.guild.id, {}).get('alone_loop')
        ):
        await voice.alone(ctx=ctx, voice_client=voice_client)

@bot.slash_command(description='Start voice call.')
async def vc(ctx):
    # Ensure it's in a guild
    if ctx.guild is None:
        await ctx.respond(f"i can only vc in servers", ephemeral=True)
        return

    # Create/retrieve voice client
    voice_client = await voice.connect(ctx=ctx)

    if not voice_client or not voice_client.is_connected():
        await ctx.respond(f"i think it broke", ephemeral=True)
        voice.connections.pop(ctx.guild.id, None)
        return 

    # Check if the bot is already in VC due to previous /vc command
    if voice.connections.get(ctx.guild.id, {}).get('state'):
        await ctx.respond("im already in vc", ephemeral=True)

    elif not voice.connections.get(ctx.guild.id, {}).get('alone_loop'):
        # Update the state to indicate the bot is in the VC due to /vc command
        voice.connections[ctx.guild.id]['state'] = True

        # Declare that the request has been acknowledged
        await ctx.respond("ok ready now", ephemeral=True)

        # Hand-off to alone() loop for idle disconnect
        await voice.alone(ctx=ctx, voice_client=voice_client)

@bot.slash_command(description='Reset the voice state in this server.')
async def reset(ctx):
    # Ensure it's in a guild
    if ctx.guild is None:
        await ctx.respond(f"i can only vc in servers", ephemeral=True)
        return

    guild_id = ctx.guild.id

    # Check if the guild is in the voice connections and remove it if present
    if guild_id in voice.connections:

        # If the bot is connected to a voice channel, disconnect it first
        voice_client = voice.connections[guild_id].get('voice_client')
        if voice_client and voice_client.is_connected():
            await voice_client.disconnect()

        # Remove the guild from connections
        voice.connections.pop(guild_id, None)

        await ctx.respond("voice state has been reset")
    else:
        await ctx.respond("there isnt anything to reset")
