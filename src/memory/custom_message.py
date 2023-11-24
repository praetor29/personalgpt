'''
CustomMessage Creator
~~~~~~~~~~~~~~~~~~~~~
Creates custom messages to insert into queue.
'''

import discord
from src.memory import memory

class CustomMessage:
    """
    Fake discord.Message clone
    """
    def __init__(self, original_message: discord.Message, new_content: str):
        self.content            = new_content
        self.clean_content      = new_content
        self.author             = original_message.author
        self.channel            = original_message.channel
        self.id                 = original_message.id
        self.created_at         = original_message.created_at
        # self.attachments      = original_message.attachments  # List of discord.Attachment objects
        # self.edited_at        = original_message.edited_at
        # self.mention_everyone = original_message.mention_everyone
        # self.mentions         = original_message.mentions  # List of User mentions
        # self.channel_mentions = original_message.channel_mentions  # List of Channel mentions
        # self.role_mentions    = original_message.role_mentions  # List of Role mentions
        # self.embeds           = original_message.embeds  # List of discord.Embed objects
        # self.reactions        = original_message.reactions  # List of discord.Reaction objects



async def slipstream(message: discord.Message, media_context: list):
    """
    Creates a fake discord.Message object, and adds it to the queue.
    """
    # Remove system context from list
    context = {
        'role'    : 'system',
        'content' : f'{message.author.display_name} uploaded an image. Here is a description of the image:',
    }
    
    descriptions = [description for description in media_context if description != context]
    
    # Enqueue custom messages
    for description in descriptions:
        # Fetch the image description text
        text    = description.get('content')
        content = f'Description of uploaded image:\n{text}'

        # Create a custom message object
        custom_message = CustomMessage(original_message=message, new_content=content)

        # Enqueue the custom message
        await memory.enqueue(message=custom_message)
