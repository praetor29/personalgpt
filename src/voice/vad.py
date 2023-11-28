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
import asyncio
import subprocess

# Import modules
from src.core import constants

class VADSink(discord.sinks.Sink):
    """
    Subclass of discord.Sink for voice activity detection.
    """

    def __init__(self, *, sample_rate: int = 48000, frame_duration: int = constants.VAD_FRAME_DURATION):
        """
        Initialize the VADSink class.

        Parameters:
            sample_rate (int)   : The sample rate of the audio.
                                  Defaults to 48000 Hz.
            frame_duration (int): The duration of each audio frame in milliseconds.
                                  Defaults to 10 ms.
        """
        super().__init__()

        # Create VAD object and define its mode
        self.vad = webrtcvad.Vad(constants.VAD_MODE)
        
        # Parameters
        self.sample_rate      = sample_rate
        self.frame_duration   = frame_duration

        # Calculate the number of frames in each audio frame
        self.number_of_frames = int(sample_rate * frame_duration / 1000)
        
        # Create a queue to hold the audio frames (humorously called playlist)
        self.playlist = asyncio.Queue()

    async def vad_loop(self) -> bool:
        """
        Primary loop for voice activity detection.
        Processes audio frames from the queue and uses VAD to detect speech.
        """
        while True:
            # Create an empty audio frame
            audio_frame = bytes()
            
            # Loop until audio fram has enough frames for duration
            while len(audio_frame) < self.number_of_frames:
                # Get audio frame from queue
                audio_frame  += await self.playlist.get()
            
            # Use VAD to detect speech
            is_speech  = await asyncio.to_thread(
                self.vad.is_speech(audio_frame, self.sample_rate)
                )
            
            if is_speech :
                # do something
                print(True)
                pass
            else:
                print(False)
                pass
    
    def write(self, data):
        """
        Handles incoming audio data from the voice channel.

        Args:
            data: The raw audio data.
        """
        # Decode and convert the data if necessary
        pcm_data = self.convert_audio(input=data)

        # Get the current event loop
        loop = asyncio.get_event_loop()

        # Schedule the put() coroutine to run soon
        loop.call_soon_threadsafe(lambda: loop.create_task(self.playlist.put(pcm_data)))



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

