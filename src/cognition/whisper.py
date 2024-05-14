'''
whisper.py
~~~~~~~~~~
Transcribes audio using the OpenAI Whisper API.
'''
'''
██╗    ██╗██╗  ██╗██╗███████╗██████╗ ███████╗██████╗ 
██║    ██║██║  ██║██║██╔════╝██╔══██╗██╔════╝██╔══██╗
██║ █╗ ██║███████║██║███████╗██████╔╝█████╗  ██████╔╝
██║███╗██║██╔══██║██║╚════██║██╔═══╝ ██╔══╝  ██╔══██╗
╚███╔███╔╝██║  ██║██║███████║██║     ███████╗██║  ██║
 ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝╚══════╝╚═╝     ╚══════╝╚═╝  ╚═╝                                                     
'''
# Import libraries
import openai
from src.core import constants

async def whisper(client: openai.AsyncOpenAI, audio) -> str:
    """
    Calls the OpenAI API to transcribe audio.

    Args:
        client (openai.AsyncOpenAI): The OpenAI client used to make API calls.
        audio: The audio file to be transcribed.

    Returns:
        str: The transcribed text.

    """
    
    # Parameters
    params = {}

    params['model']           = constants.WHISPER_MODEL
    params['file']            = audio
    params['response_format'] = 'text'
    if constants.WHISPER_LANG:
        params['language']    = constants.WHISPER_LANG
    if constants.WHISPER_PROMPT:
        params['prompt']      = constants.WHISPER_PROMPT

    return await client.audio.transcriptions.create(**params)