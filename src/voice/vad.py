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
import webrtcvad
import asyncio

# Import modules
from src.core import constants

# Create VAD object and define its mode
vad = webrtcvad.Vad(constants.VAD_MODE)

async def is_speech(audio_frame, sample_rate) -> bool:
    """
    Process a single audio frame for voice activity detection.

    Parameters:
        audio_frame: The audio frame to be processed.
        sample_rate: The sample rate of the audio frame.

    Returns:
        Boolean indicating if speech is detected in the frame.
    """
    status = await asyncio.to_thread(vad.is_speech(audio_frame, sample_rate))

    return status

