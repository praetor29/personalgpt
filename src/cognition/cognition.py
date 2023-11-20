'''
cognition
~~~~~~~~~
Cognitive functions using API requests.
'''
'''
 ██████╗ ██████╗  ██████╗ ███╗   ██╗██╗████████╗██╗ ██████╗ ███╗   ██╗
██╔════╝██╔═══██╗██╔════╝ ████╗  ██║██║╚══██╔══╝██║██╔═══██╗████╗  ██║
██║     ██║   ██║██║  ███╗██╔██╗ ██║██║   ██║   ██║██║   ██║██╔██╗ ██║
██║     ██║   ██║██║   ██║██║╚██╗██║██║   ██║   ██║██║   ██║██║╚██╗██║
╚██████╗╚██████╔╝╚██████╔╝██║ ╚████║██║   ██║   ██║╚██████╔╝██║ ╚████║
 ╚═════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝                                                                                                                                  
'''

# Import libraries
from openai import AsyncOpenAI
# Import modules
from src.core import constants

# Initialize client with openai key
client = AsyncOpenAI(api_key=constants.OPENAI)

async def chat_completion(user_message: str) -> str:
    """
    Sends and receives a response from AsyncOpenAI API.
    """

    response = await client.chat.completions.create(
        messages=[
            {
                'role': 'user',
                'content': f'{user_message}',
            }
        ],
        model='ft:gpt-3.5-turbo-1106:personal::8Ibhmf2N',
    )
    
    return response.choices[0].message.content

