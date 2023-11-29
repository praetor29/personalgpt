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
    VAD Subclass of Sink.
    """
    def __init__(self, *, filters=None):
        super().__init__() # Initialize parent class

        # Create VAD object and define its mode
        self.vad = webrtcvad.Vad(constants.VAD_MODE)
        
        # Parameters
        self.sample_rate = 48000
        self.frame_duration = constants.VAD_FRAME_DURATION  # Frame duration in milliseconds

        # Calculate the number of samples in each audio frame
        self.number_of_samples = int(self.sample_rate * self.frame_duration / 1000)  # Number of samples per frame
        
        # Calculate the size of each audio frame in bytes
        self.frame_size = self.number_of_samples * 2
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        # Create a queue to hold the audio frames (aka playlist)
        self.playlist = asyncio.Queue()
        
        # Obtain event loop
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

    def format_audio(self, audio: bytes) -> bytes:
        """
        Efficient audio conversion to webrtcvad compatible format.
        (PCM, self.sample_rate Hz, 16-bit, mono)
        Uses ffmpeg natively for efficiency.
        """
        # Declare ffmpeg command for downsampling
        ffmpeg = [
            'ffmpeg',
            '-f', 's16le',  # Specify the format of the input data
            '-ar', '96000', # Input sample rate
            '-ac', '1',     # Input is mono
            '-i', 'pipe:0', # Input from stdin
            '-ar', '48000', # Output sample rate (downsample to 48kHz)
            '-acodec', 'pcm_s16le',  # PCM codec for output
            '-f', 's16le',  # Specify the format of the output data
            'pipe:1'  # Output to stdout
        ]

        # Run process under a context manager
        with subprocess.Popen(ffmpeg,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        ) as process:
            # Send the audio data to FFmpeg and get the converted data
            output, error = process.communicate(input=audio)

        if process.returncode != 0:
            print(f"FFmpeg error: {error.decode('utf8')}")
        
        if output:
            return output
        else:
            print("Conversion failed, output is None")

    async def vad_loop(self) -> bool:
        """
        Primary loop for voice activity detection.
        Processes audio frames from the queue and uses VAD to detect speech.
        """
        buffer = bytearray()  # Buffer to store incoming audio data as a mutable bytearray

        while True:
            # Wait for the next item from the playlist
            raw  = await self.playlist.get()

            # Convert audio frame to webrtcvad compatible format
            data = self.format_audio(raw)
            
            # Append new data to the buffer
            buffer.extend(data)

            while len(buffer) >= self.frame_size:
                # Extract one frame from the buffer
                webrtc_frame = buffer[:self.frame_size ]

                # Remove the processed frame from the buffer
                buffer = buffer[self.frame_size:]
                       
                if webrtc_frame:
                    is_speech = await asyncio.to_thread(
                        self.vad.is_speech, webrtc_frame, self.sample_rate
                    )
                    print(is_speech)
    
    def save_audio_data(self, audio_data: bytes, filename: str):
        """
        Saves raw audio data to a file for verification purposes.
        
        Args:
            audio_data: The raw audio data to save.
            filename: The name of the file to save the data to.
        """
        with open(filename, 'ab') as f:  # 'ab' mode to append binary data
            f.write(audio_data)
            print(f"Data written to {filename}")
                         