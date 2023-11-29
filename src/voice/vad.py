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
        self.frame_duration_ms = constants.VAD_FRAME_DURATION  # Frame duration in milliseconds

        # Calculate the number of samples in each audio frame
        self.number_of_samples = int(self.sample_rate * self.frame_duration_ms / 1000)  # Number of samples per frame

        # Calculate frame length in bytes (16-bit audio = 2 bytes per sample)
        self.frame_length_in_bytes = self.number_of_samples * 2
        
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
        # Declare ffmpeg command
        ffmpeg = [
            'ffmpeg',
            '-f', 's16le',  # Specify the format of the input data
            '-i', 'pipe:0',  # Input from stdin
            '-f', 's16le',  # Specify PCM format for output
            '-ar', '48000',  # Sample rate
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
            output, error = process.communicate(input=audio)

        if process.returncode != 0:
            raise Exception(f"FFmpeg error: {error.decode('utf8')}")
        
        print(f"Input data size: {len(audio)} bytes")
        if output:
            print(f"Converted data size: {len(output)} bytes")
        else:
            print("Conversion failed, output is None")

        return output

    async def vad_loop(self) -> bool:
        """
        Primary loop for voice activity detection.
        Processes audio frames from the queue and uses VAD to detect speech.
        """
        buffer = bytes()  # Buffer to store incoming audio data

        while True:
            buffer += await self.playlist.get()

            # Process complete frames in the buffer
            while len(buffer) >= self.frame_length_in_bytes:
                # Extract one frame from the buffer
                audio_frame = buffer[:self.frame_length_in_bytes]
                buffer = buffer[self.frame_length_in_bytes:]

                # Convert audio frame to webrtcvad compatible format
                webrtc_frame = self.format_audio(audio_frame)

                if webrtc_frame:

                    # Check if the frame size after conversion is correct
                    if len(webrtc_frame) == self.frame_length_in_bytes:
                        is_speech = await asyncio.to_thread(
                            self.vad.is_speech, webrtc_frame, self.sample_rate
                        )
                        print(is_speech)
                    else:
                        print("Converted frame size incorrect, skipping frame")

                        