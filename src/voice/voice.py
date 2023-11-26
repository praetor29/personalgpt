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
from elevenlabs import set_api_key, Voice, VoiceSettings, generate
from io import BytesIO
import asyncio
import discord

# Import modules
from src.core import constants
from src.core import utility

# Declare API key
set_api_key(constants.ELEVENLABS)

'''
ElevenLabs API Call
'''

async def tts(message):
    """
    Uses ElevenLabs to asynchronously run TTS.
    """
    # Await audio data in a non-blocking thread
    audio = await asyncio.to_thread(
    generate, # ElevenLabs function

    # Parameters
    text  = message,
    model = constants.VOICE_MODEL,
    voice = Voice(
        voice_id = constants.VOICE_ID,
        settings = VoiceSettings(
            stability         = constants.VOICE_STABILITY,
            similarity_boost  = constants.VOICE_SIMILARITY,
            style             = constants.VOICE_STYLE,
            use_speaker_boost = constants.VOICE_BOOST,
            )
        ),
    )
    
    # Convert audio to Discord compatible format (uses a non-blocking thread)
    converted_audio = await asyncio.to_thread(utility.convert_audio, audio=audio)
    
    return converted_audio

'''
VC Functions
'''

async def connect(ctx) -> discord.VoiceClient:
    """
    Checks if connected.
    Connects if not.
    Returns state.
    """
    # If bot already in VC, return VC
    if ctx.voice_client:
        voice_client = ctx.voice_client
        return voice_client
    
    else:
        # If user in VC, connect to that VC
        if ctx.author.voice:
             channel = ctx.author.voice.channel
             try:
                voice_client = await channel.connect()
                return voice_client
             except Exception as e:
                 await ctx.respond(f'Error connecting to channel: `{e}`', ephemeral=True)  
                 return False              
        else:
            # Ask user to connect to VC
            await ctx.respond(f'join vc so i can join', ephemeral=True)
            return False

async def speak(ctx, message: str):
    """
    Allows the bot to connect to VC and speak.
    """
    try:
        # Retrieve channel
        voice_client = await connect(ctx=ctx)
        
        # Exit if failed to get voice client
        if not voice_client:
            return   

        # Synthesize text-to-speech
        audio_data = await tts(message)

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
            await ctx.respond(f'Error playing audio: `{error}`', ephemeral=True)
        
        # Plays audio
        voice_client.play(audio_source, after=after_playing)
        
        # Wait for the audio to finish playing
        await play_audio.wait()  

    except Exception as e:
        await ctx.respond(f'An error occured: `{e}`', ephemeral=True) 

    finally:
        # Disconnect from the voice channel
        if voice_client and voice_client.is_connected():
            await voice_client.disconnect()