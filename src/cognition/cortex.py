"""
memory processing
~~~~~~~~~~~~~~~~~
"""

import discord
from src.cognition.memory import cache
from src.core import constants
from src.core.utility import verify_media


async def constructor(message: discord.Message) -> list:
    """
    Constructs the uplink list.
    """
    # Construct system prompt
    uplink = [
        {
            "role": "system",
            "content": constants.CHAT_PROMPT,
        },
    ]

    # Fetch conversation context from memory queue
    context = await assembler(message=message)
    # Augment uplink with context
    uplink.extend(context)

    return uplink


async def assembler(message: discord.Message) -> list:
    """
    Assembles the context.
    """
    # Fetch queue from cache
    queue = await cache.get(message.channel.id) or []

    # Assemble
    collection = []
    for msg in queue:
        # Check if bot's message or user's
        if msg.author.id == constants.BOT_ID:
            role = "assistant"
        else:
            role = "user"

        name_dict = {
            "role": "system",
            "content": f"{msg.author.display_name}:",
        }

        message_dict = {
            "role": role,
            "content": msg.clean_content,
        }

        # Media handler
        if msg.attachments:
            media = await verify_media(message=msg)
            if media:
                content = []

                # Add text in message
                body = {
                    "type": "text",
                    "text": msg.clean_content,
                }
                content.append(body)

                # Add images
                for attachment in media:
                    # Components of the request
                    image = {
                        "url": attachment.url,
                        "detail": constants.VISION_DETAIL,
                    }
                    content.append(image)

                message_dict["content"] = content

        # Add to construction list
        collection.append(name_dict)
        collection.append(message_dict)

    return collection
