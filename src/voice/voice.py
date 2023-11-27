'''
voice
~~~~~
Centralized voice management.
'''
'''
██╗   ██╗ ██████╗ ██╗ ██████╗███████╗
██║   ██║██╔═══██╗██║██╔════╝██╔════╝
██║   ██║██║   ██║██║██║     █████╗  
╚██╗ ██╔╝██║   ██║██║██║     ██╔══╝  
 ╚████╔╝ ╚██████╔╝██║╚██████╗███████╗
  ╚═══╝   ╚═════╝ ╚═╝ ╚═════╝╚══════╝                                                                                               
'''

# Import libraries
from io import BytesIO
import asyncio
import discord

# Import modules
from src.voice import tts
from src.core import constants

'''
VC Functions
'''

# Holds guilds, and their respective voice channels, alone flags, and VC states (T/F)
connections = {}

async def connect(ctx):
    """
    Checks if connected.
    Connects if not.
    Returns state.
    """

    guild_id = ctx.guild.id

    # Check if supposedly connected, but the voice client is not actually connected
    if guild_id in connections:
        voice_client = connections.get(guild_id, {}).get('voice_client')
        if voice_client and not voice_client.is_connected():
            # Reset the state if the bot is not actually connected
            connections.pop(guild_id, None)

    # If bot already in guild VC, return the existing voice client
    if guild_id in connections:
        return connections[guild_id]['voice_client']

    # If user in VC, connect to that VC
    if ctx.author.voice:
        channel = ctx.author.voice.channel

        try:
            voice_client = await channel.connect()

            # Update connections
            connections[guild_id] = {
                'voice_client': voice_client,
                'state'       : False,
                'alone_loop'  : False,
            }
            return voice_client

        except Exception as e:
            await ctx.respond(f'Error connecting to channel: `{e}`', ephemeral=True)
            return False
    else:
        # Ask user to connect to VC
        await ctx.respond(f'you have to join vc first', ephemeral=True)
        return False

# async def alone(ctx, voice_client: discord.VoiceClient):
#     """
#     Disconnects if alone in VC for more than the idle time.
#     Has grace periods implemented.
#     """
#     # Initialize the entry if it doesn't exist
#     if ctx.guild.id not in connections:
#         connections[ctx.guild.id] = {
#             'voice_client': voice_client,
#             'state'       : False,
#             'alone_loop'  : False
#         }

#     while True:
#         connections[ctx.guild.id]['alone_loop'] = True

#         # Check regularly to be responsive
#         await asyncio.sleep(5)
        
#         # Check if connected to VC at all. If not, break.
#         ## Safeguard check against exceptions
#         if not voice_client or not voice_client.is_connected():
#             connections[ctx.guild.id]['alone_loop'] = False
#             break
        
#         # Number of members in vc
#         members = len(voice_client.channel.members)

#         # Check if alone in vc
#         if members == 1:
#             # Begin grace period
#             await asyncio.sleep(constants.VOICE_IDLE)
            
#             # Final check
#             if members == 1:
#                 await ctx.respond(f"goodbye", ephemeral=True)
                
#                 # Disconnect and update connections
#                 await voice_client.disconnect()
#                 connections.pop(ctx.guild.id, None)
                
#                 break

async def alone(ctx, voice_client: discord.VoiceClient):
    """
    Disconnects if alone in VC for more than the idle time.
    Has grace periods implemented.
    """
    guild_id = ctx.guild.id

    # Initialize the entry if it doesn't exist
    if guild_id not in connections:
        connections[guild_id] = {
            'voice_client': voice_client,
            'state'       : False,
            'alone_loop'  : False
        }
    else:
        # Set the flag when entering the loop
        connections[guild_id]['alone_loop'] = True

    while True:
        # Check if connected to VC at all. If not, break and reset state.
        ## Safeguard check against exceptions
        if not voice_client or not voice_client.is_connected():
            if guild_id in connections:
                connections[guild_id]['alone_loop'] = False
            break
        
        # Number of members in vc
        members = len(voice_client.channel.members)

        # Check if alone in vc
        if members == 1:
            # Begin grace period
            await asyncio.sleep(constants.VOICE_IDLE)
            
            # Recheck the member count and if still alone, disconnect
            if len(voice_client.channel.members) == 1:
                await ctx.respond(f"goodbye", ephemeral=True)
                
                # Disconnect and update connections
                await voice_client.disconnect()
                
                # Safely remove the guild from connections if it exists
                connections.pop(guild_id, None)
                
                break
        else:
            # If the bot is not alone, continue the loop
            await asyncio.sleep(5)

'''
VC Features
'''

async def read(ctx, voice_client: discord.VoiceClient, text: str):
    """
    Allows the bot to connect to VC and speak.
    """
    try:
        # Synthesize text-to-speech and retrieve bytes
        audio_data = await tts.tts(text)

        # Create discord audio source
        audio_source = discord.PCMAudio(BytesIO(audio_data))
        
        # Create event to play audio
        play_audio = asyncio.Event()           
        
        def after_playing(error):
            if error:
                # Schedule the execution of a coroutine function to handle the error
                asyncio.create_task(handle_error(error))
            # Signals end of audio playing
            play_audio.set()
        
        async def handle_error(error):
            # Now you can await inside this function
            await ctx.respond(f'error playing audio: `{error}`', ephemeral=True)
        
        # Plays audio
        voice_client.play(audio_source, after=after_playing)
        
        # Wait for the audio to finish playing
        await play_audio.wait()  

    except Exception as e:
        await ctx.respond(f'an error occured: `{e}`', ephemeral=True)