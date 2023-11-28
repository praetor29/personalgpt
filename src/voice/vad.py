'''
Voice Activity Detection (VAD) functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
'''
██╗   ██╗ █████╗ ██████╗ 
██║   ██║██╔══██╗██╔══██╗
██║   ██║███████║██║  ██║
╚██╗ ██╔╝██╔══██║██║  ██║
 ╚████╔╝ ██║  ██║██████╔╝
  ╚═══╝  ╚═╝  ╚═╝╚═════╝ 
'''

# Import libraries
import discord
import webrtcvad
from queue import Queue
import asyncio
import subprocess
import io

# Import modules
from src.core import constants

class VADSink(discord.sinks.Sink):
    """
    VAD Subclass of Sink.
    """
    def __init__(self, *, filters=None):
        super().__init__() # Initialize parent class

        # Create VAD object and define its mode
        self.vad = webrtcvad.Vad(constants.VAD_MODE)
        
        # Parameters
        self.sample_rate      = 48000
        self.frame_duration   = constants.VAD_FRAME_DURATION

        # Calculate the number of frames in each audio frame
        self.number_of_frames = int(self.sample_rate * self.frame_duration / 1000)
        
        # Create a queue to hold the audio frames (aka playlist)
        self.playlist = asyncio.Queue()

        self.loop = asyncio.get_event_loop()
   
    def write(self, data, user):
        """
        Handles incoming audio data from the voice channel.

        Args:
            data: The raw audio data.
            user: The user who sent the audio data.
        """
        # Push data to playlist
        asyncio.run_coroutine_threadsafe(self.playlist.put(data), self.loop)

    def convert_audio(self, input: bytes) -> bytes:
        """
        Efficient audio conversion to webrtcvad compatible format.
        (PCM, self.sample_rate Hz, 16-bit, mono)
        Uses ffmpeg natively for efficiency.
        """
        # Declare ffmpeg command
        ffmpeg = [
            'ffmpeg',
            '-i', 'pipe:0',  # Input from stdin
            '-f', 's16le',  # PCM format
            '-ar', str(self.sample_rate),  # Sample rate 48kHz
            '-ac', '1',  # Mono
            '-acodec', 'pcm_s16le',  # PCM codec
            'pipe:1'  # Output to stdout
        ]

        # Run process under a context manager
        with subprocess.Popen(ffmpeg,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        ) as process:
            # Send the audio data to FFmpeg and get the converted data
            output, error = process.communicate(input=input)

        if process.returncode != 0:
            raise Exception(f"FFmpeg error: {error.decode('utf8')}")

        return output
        
    def format_audio(self, audio):
        """
        Formats the recorded audio.
        """
        args = [
            "ffmpeg",
            "-f",
            "s16le",
            "-ar",
            "48000",
            "-loglevel",
            "error",
            "-ac",
            "2",
            "-i",
            "-",
            "-f",
            "ogg",
            "pipe:1",
        ]
        try:
            process = subprocess.Popen(
                args,
                creationflags=CREATE_NO_WINDOW,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
            )
        except FileNotFoundError as e:
            print(f"ffmpeg was not found: {e}")
        except subprocess.SubprocessError as exc:
            print("Popen failed: {0.__class__.__name__}: {0}".format(exc))

        out = process.communicate(audio.file.read())[0]
        out = io.BytesIO(out)
        out.seek(0)
        audio.file = out
        audio.on_format(self.encoding)

    async def vad_loop(self) -> bool:
        """
        Primary loop for voice activity detection.
        Processes audio frames from the queue and uses VAD to detect speech.
        """
        while True:
            # # Create an empty audio frame
            # audio_frame = bytes()
            
            # # Loop until audio fram has enough frames for duration
            # while len(audio_frame) < self.number_of_frames:
            #     # Get audio frame from queue
            #     audio_frame  += await self.playlist.get()
            
            # # Use VAD to detect speech
            # is_speech  = await asyncio.to_thread(
            #     self.vad.is_speech(audio_frame, self.sample_rate)
            #     )
            
            # if is_speech :
            #     # do something
            #     print(True)
            #     pass
            # else:
            #     print(False)
            #     pass
            try:
                data = await self.playlist.get()
                print(data)
            except Exception as e:
                print(f"Error in vad_loop: {e}")