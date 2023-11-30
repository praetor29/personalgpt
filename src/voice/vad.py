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
        """
        Initializes the VAD (Voice Activity Detection) object.

        Args:
            filters (optional): Filters to be applied during VAD. Defaults to None.
        """
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

        '''
        VAD STATE
        '''
        self.state = False
   
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

        Args:
            audio (bytes): The input audio data to be converted.

        Returns:
            bytes: The converted audio data in the specified format.

        Raises:
            None

        Notes:
            - The input audio data should be in PCM format.
            - The input sample rate should be 96 kHz.
            - The output sample rate will be downsampled to self.sample_rate (48 kHz).
            - The output audio data will be in 16-bit, mono format.
            - If the conversion fails, None will be returned.

        !! Caution: pycord outputs data at 96 kHz for some reason, so this is static.
          No idea why this is the case, but it works so I'm not complaining.
        """
        # Declare ffmpeg command for downsampling
        ffmpeg = [
            'ffmpeg',
            '-f', 's16le',  # Specify the format of the input data
            '-ar', '96000', # Input sample rate
            '-ac', '1',     # Input is mono
            '-i', 'pipe:0', # Input from stdin
            '-ar', str(self.sample_rate), # Output sample rate (downsample to 48kHz)
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

            Returns:
                bool: True if speech is detected, False otherwise.
            """
            buffer = bytearray()  # Buffer to store incoming audio data as a mutable bytearray

            while self.vc.recording:
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
                        # Set the VAD state based on input frame
                        self.state = await asyncio.to_thread(
                            self.vad.is_speech, webrtc_frame, self.sample_rate
                        )

