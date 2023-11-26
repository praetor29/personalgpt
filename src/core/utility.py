'''
utility
~~~~~~~
A collection of utility functions.
'''
'''
██╗   ██╗████████╗██╗██╗     ██╗████████╗██╗   ██╗
██║   ██║╚══██╔══╝██║██║     ██║╚══██╔══╝╚██╗ ██╔╝
██║   ██║   ██║   ██║██║     ██║   ██║    ╚████╔╝ 
██║   ██║   ██║   ██║██║     ██║   ██║     ╚██╔╝  
╚██████╔╝   ██║   ██║███████╗██║   ██║      ██║   
 ╚═════╝    ╚═╝   ╚═╝╚══════╝╚═╝   ╚═╝      ╚═╝                                              
'''

# Import libraries
import os
import tiktoken
import subprocess

def clear():
    """
    Clears the console screen.

    This function uses the operating system's command to clear the console screen. 
    It detects the operating system and uses 'cls' for Windows ('nt') and 'clear' for Unix-based systems.
    """
    os.system('cls' if os.name == 'nt' else 'clear')

async def tokenize(input: str) -> int:
    """
    Tokenize strings using tiktoken's 'cl100k_base'.
    Works with gpt-4, gpt-3.5-turbo, text-embedding-ada-002.
    """
    encoding = tiktoken.get_encoding('cl100k_base').encode(input)
    tokens   = len(encoding)
    return tokens

async def simple_tokenize(input: str) -> int:
    """
    Tokenize strings using a simple approximation:
    1 token = 4 characters.
    """
    tokens   = len(input) // 4
    return tokens  

def convert_audio(audio: bytes) -> bytes:
    """
    Efficient audio conversion to Discord compatible PCM format.
    Uses ffmpeg natively for efficiency.
    """
    # Declare ffmpeg command
    ffmpeg = [
        'ffmpeg',
        '-i', 'pipe:0',  # Input from stdin
        '-f', 's16le',  # PCM format
        '-ar', '48000',  # Sample rate 48kHz
        '-ac', '2',  # Stereo
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

    return output

