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
import wave
import io
from contextlib import contextmanager

# Import modules
from src.core import constants
from src.cognition import cognition

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

        # Obtain event loop
        self.loop = asyncio.get_event_loop()
        
        '''
        Audio Parameters
        '''
        # Parameters
        self.sample_rate = 48000
        self.frame_duration = constants.VAD_FRAME_DURATION  # Frame duration in milliseconds

        # Calculate the number of samples in each audio frame
        self.number_of_samples = int(self.sample_rate * self.frame_duration / 1000)  # Number of samples per frame
        
        # Calculate the size of each audio frame in bytes
        self.frame_size = self.number_of_samples * 2
        
        '''
        Queues
        '''
        # Create a queue to hold the audio frames (aka playlist)
        self.playlist = asyncio.Queue()
        
        # Create a queue to hold the active audio frames for trancription
        self.active   = asyncio.Queue()

        '''
        VAD STATE
        '''
        # self.live_state = False
        self.state      = False
        self.hold       = False

        # Thresholds
        self.threshold  = constants.VAD_SMOOTHING
        # Counts
        self.true_count  = 0
        self.false_count = 0
   
    def write(self, data, user):
        """
        Handles incoming audio data from the voice channel.

        Args:
            data: The raw audio data.
            user: The user who sent the audio data.
        """
        # Push data to playlist only if hold is not active
        if not self.hold:
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

    async def vad_loop(self):
            """
            Primary loop for voice activity detection.
            Processes audio frames from the queue and uses VAD to detect speech.

            Returns:
                bool: True if speech is detected, False otherwise.
            """           
            buffer = bytearray()  # Buffer to store incoming audio data as a mutable bytearray
            
            while self.vc.recording:
                try:
                    # <<< Wait for the next item from the playlist with timeout (1 sec)
                    raw = await asyncio.wait_for(self.playlist.get(), 1)
                except asyncio.TimeoutError:
                    # Playlist is effectively empty, set state to False
                    self.state = False
                    await self.transcribe()
                    continue  # Skip the rest of the loop and wait for new data

                # Convert audio frame to webrtcvad compatible format
                data = self.format_audio(raw)
                
                # >>> Send to active queue if state is True
                if self.state:
                    await self.active.put(data)

                # Append new data to the buffer
                buffer.extend(data)

                while len(buffer) >= self.frame_size:
                    # Extract one frame from the buffer
                    webrtc_frame = buffer[:self.frame_size ]

                    # Remove the processed frame from the buffer
                    buffer = buffer[self.frame_size:]
                           
                    if webrtc_frame:
                        # Set the VAD state based on input frame
                        verdict = await asyncio.to_thread(
                            self.vad.is_speech, webrtc_frame, self.sample_rate
                        )

                        # Smooth the VAD state
                        await self.smooth_state(verdict)
        
    async def smooth_state(self, verdict: bool):
        """
        Provides smoothing to the output of vad_loop().
        """

        # True Logic
        if verdict:
            self.true_count += 1 # Increment true count
            self.false_count = 0 # Reset false count

            if self.true_count >= self.threshold:
                self.state = True
        
        # False Logic
        else:
            self.false_count += 1 # Increment false count
            self.true_count   = 0 # Reset true count

            if self.false_count >= self.threshold:
                self.state = False
    
    @contextmanager
    def hold_manager(self):
        try:
            self.hold = True
            yield
        finally:
            self.hold = False

    async def transcribe(self):
            """
            Transcribe active buffer.

            This method transcribes the audio data from the active buffer. It collects frames while speech is detected,
            processes the frames when speech ends, and then transcribes the audio using the `cognition.transcribe` method.

            Raises:
                Exception: If an error occurs during the transcription process.
            """
            if self.active.empty():
                return
            
            try:
                print('entered transcribe()')
                with self.hold_manager():
                    print(f'Hold state: {self.hold}')

                    frames = []
                    while not self.active.empty():
                        frame = await self.active.get()
                        # Ensure frame is bytes-like object
                        if isinstance(frame, bytes):
                            frames.append(frame)
                        else:
                            print("Frame is not a bytes-like object")
                    
                    clip = b''.join(frames)

                    # Create a memory file to store the audio data
                    with io.BytesIO() as memfile:
                        print('created memfile')
                        # Create a wave file writer
                        with wave.open(memfile, 'wb') as wav_file:
                            wav_file.setnchannels(1)  # Mono channel
                            wav_file.setsampwidth(2)  # PCM 16 bit
                            wav_file.setframerate(self.sample_rate)
                            wav_file.writeframes(clip)
                            print('wrote frames to wav_file')

                        memfile.seek(0)  # Rewind the buffer
                        print('seeked memfile')

                        output_path = 'transcription_input.wav'
                        with open(output_path, 'wb') as f:
                            f.write(memfile.read())

                        audio_file = open('transcription_input.wav', "rb")

                        '''
                        TRANSCRIBE MEMFILE
                        '''
                        transcription = await cognition.transcribe(audio=audio_file)
                        
                        print()
                        print(transcription)
                        print()
                
                print(f'Hold state: {self.hold}')

            except Exception as e:
                print(f'VADSink transcribe() error: {e}')









