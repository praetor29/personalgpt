'''
text-to-speech (TTS) functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
'''
████████╗████████╗███████╗
╚══██╔══╝╚══██╔══╝██╔════╝
   ██║      ██║   ███████╗
   ██║      ██║   ╚════██║
   ██║      ██║   ███████║
   ╚═╝      ╚═╝   ╚══════╝                          
'''

# Import libraries
from elevenlabs import set_api_key, Voice, VoiceSettings, generate
import asyncio

# Import modules
from src.core import constants
from src.core import utility

# Declare API key
set_api_key(constants.ELEVENLABS)

async def tts(message) -> bytes:
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

    # TODO: use discord.FFmpegOpusAudio() instead of converting manually!!
    
    return converted_audio