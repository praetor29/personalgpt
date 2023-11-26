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
import discord
import asyncio
from io import BytesIO
from elevenlabs import set_api_key, Voice, VoiceSettings, generate
from src.core import constants

set_api_key(constants.ELEVENLABS)

# async def tts(text) -> AsyncIterator[bytes]:
#     """
#     Uses ElevenLabs to asynchronously run TTS.
#     """
#     async for audio_chunk in await agenerate(
#     text   = text,
#     stream = True,

#     # Parameters
#     model  = constants.VOICE_MODEL,
#     voice  = Voice(
#         voice_id = constants.VOICE_ID,
#         settings = VoiceSettings(
#             stability         = constants.VOICE_STABILITY,
#             similarity_boost  = constants.VOICE_SIMILARITY,
#             style             = constants.VOICE_STYLE,
#             use_speaker_boost = constants.VOICE_BOOST,
#             )
#         ),
#     ):
#         yield audio_chunk

# CUSTOM CLASS???
# from collections import deque
# from threading import Event

# class AsyncQueueAudioSource(discord.AudioSource):
#     def __init__(self):
#         self.queue = deque()
#         self.done_playing = Event()

#     def read(self):
#         if not self.queue:
#             self.done_playing.wait()
#             self.done_playing.clear()

#         return self.queue.popleft()

#     def write(self, data):
#         self.queue.append(data)
#         self.done_playing.set()

# async def speak(ctx):
#     text = "Hello world, this is a test. Blah blah blah, morgan himes, blah blah, this is so complex."

#     if ctx.author.voice:
#         channel = ctx.author.voice.channel
#         voice_client = await channel.connect()

#     source = AsyncQueueAudioSource()
#     voice_client.play(source)

#     try:
#         async for audio_chunk in tts(text):
#             source.write(audio_chunk)
#             while source.queue:  # Wait for the chunk to be consumed
#                 await asyncio.sleep(0.2)
#     finally:
#         if voice_client.is_connected():
#             await voice_client.disconnect()

from pydub import AudioSegment

def convert_audio(audio_data, source_format="mp3"):
    # Load the audio data using the appropriate format
    audio_segment = AudioSegment.from_file(BytesIO(audio_data), format=source_format)

    # Convert the audio to the desired format (48kHz, stereo, 16-bit)
    converted_audio = audio_segment.set_frame_rate(48000).set_channels(2).set_sample_width(2)

    # Export the converted audio to bytes
    buffer = BytesIO()
    converted_audio.export(buffer, format="wav")
    return buffer.getvalue()


async def tts(text):
    """
    Uses ElevenLabs to asynchronously run TTS.
    """
    audio = await asyncio.to_thread(generate,
    text   = text,
    stream = False,

    # Parameters
    model  = constants.VOICE_MODEL,
    voice  = Voice(
        voice_id = constants.VOICE_ID,
        settings = VoiceSettings(
            stability         = constants.VOICE_STABILITY,
            similarity_boost  = constants.VOICE_SIMILARITY,
            style             = constants.VOICE_STYLE,
            use_speaker_boost = constants.VOICE_BOOST,
            )
        ),
    )

    converted_audio = await asyncio.to_thread(
        convert_audio,
        audio_data=audio,
        source_format="mp3"  # Adjust the format if different
    )
    
    return converted_audio

async def speak(ctx):
    text = "Hello world, this is a test. Blah blah blah, morgan himes, blah blah, this is so complex."

    if ctx.author.voice:
        channel = ctx.author.voice.channel
        voice_client = await channel.connect()
    
    audio_data = await tts(text)  # Await the entire audio data

    audio_source = discord.PCMAudio(BytesIO(audio_data))
    voice_client.play(audio_source)

    while voice_client.is_playing():
        await asyncio.sleep(1)

    if voice_client.is_connected():
        await voice_client.disconnect()

