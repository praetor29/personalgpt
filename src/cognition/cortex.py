"""
memory processing
~~~~~~~~~~~~~~~~~
"""

import discord
from src.cognition.memory import cache
from src.core import constants
from src.core.utility import verify_media

import aiohttp
import base64


async def constructor(message: discord.Message) -> list:
    """
    Constructs the uplink list.
    """
    # Construct system prompt
    prompt = {
        "type": "text",
        "text": constants.CHAT_PROMPT,
    }
    uplink = [
        {
            "role": "system",
            "content": [prompt] if prompt["text"] else [],
        },
    ]

    # Fetch conversation context from memory queue
    context = await assembler(message=message)
    # Augment uplink with context
    uplink.extend(context)

    return uplink


async def imgcoder(url: str) -> str:
    """
    Fetch an image from a URL and encode it as a Base64 string.
    Returns the image in the format: "data:image/png;base64,<base64_string>"
    """
    try:
        async with aiohttp.ClientSession() as session:

            async with session.get(url) as response:
                if response.status == 200:
                    image_data = await response.read()
                    base64_image = base64.b64encode(image_data).decode("utf-8")
                    return f"data:image/png;base64,{base64_image}"

                else:
                    return None

    except Exception as e:
        return None


async def assembler(message: discord.Message) -> list:
    """
    Assembles the context.
    """
    # Fetch queue from cache
    queue = await cache.get(message.channel.id) or []

    # Assemble
    collection = []
    for msg in queue:
        # Determine the role
        role = "assistant" if msg.author.id == constants.BOT_ID else "user"

        author_name = {
            "type": "text",
            "text": f"{msg.author.display_name} said:",
        }
        name_dict = {
            "role": "system",
            "content": [author_name] if author_name["text"] else [],
        }

        # --------------------------------------------------------------------
        # Add text to message dictionary
        body = {
            "type": "text",
            "text": msg.clean_content,
        }

        # Initial message dictionary
        message_dict = {
            "role": role,
            "content": [body] if body["text"] else [],
        }

        # --------------------------------------------------------------------

        # Check for attachments and handle media
        if msg.attachments:
            media = await verify_media(msg)
            if media:
                # Add images as URLs
                for attachment in media:
                    image_url = {}

                    # Base64 encode image
                    if attachment.url:
                        image_url["url"] = await imgcoder(attachment.url)
                    elif attachment.proxy_url:
                        image_url["url"] = await imgcoder(attachment.proxy_url)
                    else:
                        # If no URL is available, skip this attachment
                        continue

                    # Guard clause: image retrieval failed
                    if not image_url["url"]:
                        continue  # Skip this attachment

                    # With successful image retrieval, add encoded image to message
                    image_dict = {
                        "type": "image_url",
                        "image_url": image_url,
                    }
                    message_dict["content"].append(image_dict)

        # --------------------------------------------------------------------
        # Add to construction list
        if message_dict["content"]:
            collection.append(name_dict)
            collection.append(message_dict)

    return collection
