'''
+------------------------------------------------------------------+
| Title      : Personal GPT                                        |
| Author     : Pranav Chiploonkar (@praetor29)                     |
+------------------------------------------------------------------+
| Description: This program runs the core loop of the discord bot. |
+------------------------------------------------------------------+
'''

# Import functions and constants
import constants
import utility
import cognition
import discord
import memory
import sys
from errors.handler import handle_exception

# Initialized flag
initialized = False

'''
Declare intents
'''
intents = discord.Intents.default()
intents.message_content = True

'''
Initialize discord bot
'''
bot = discord.Client(intents=intents)

'''
Confirm login
Change status and activity
'''
@bot.event
async def on_ready():
    '''
    Memory Management
    '''
    # Initialize LongTermMemory
    print('>> Initializing LongTermMemory...')
    global LongTermMemory
    LongTermMemory  = memory.LongTermMemory()

    # Initialize ShortTermMemory
    print('>> Initializing ShortTermMemory...')
    global ShortTermMemory
    ShortTermMemory = memory.ShortTermMemory(LTM=LongTermMemory)
    
    '''
    Database Management
    '''
    # Stuff
    print('>> Cleaning up database...')
    
    # Enable rich presence
    print('>> Setting up bot presence...')
    await bot.change_presence(
        status   = constants.STATUS,
        activity = discord.Activity(
        type     = constants.ACTIVITY_TYPE,
        name     = constants.ACTIVITY_NAME,
        )
    )
    # Login message
    login = f'Successfully logged in as {bot.user}.'
    print('\n+-' + '-' * len(login) + '-+'  )
    print(f'| {login} |')
    print(  '+-' + '-' * len(login) + '-+\n')

    # Set initialized flag to True
    global initialized
    initialized = True

'''
Bot functioning
'''
@bot.event
async def on_message(message):
    # Return if not initialized
    global initialized
    if not initialized:
        return

    # Prepare user_message for API call
    user_message   = utility.stripper(message.clean_content.strip())

    '''Response loop when mentioned.'''
    if bot.user in message.mentions:
        # Ignore own messages
        if message.author == bot.user:
            return

        async with message.channel.typing(): # Show typing indicator
            # Fetch recent messages from Short Term Memory
            recent             = await ShortTermMemory.get_raw_n(id=message.channel.id, n_recent=constants.RECENT_CONTEXT)
            # Determine the current topic
            topic = await cognition.topic(recent=recent)
            # Returns a list of similar message indices
            similar_indices    = await LongTermMemory.similarity(
                                    topic=topic, guild_id=message.guild.id, channel_id=message.channel.id)
            similar_messages   = await LongTermMemory.similarity_SQL(
                                    indices=similar_indices, guild_id=message.guild.id, channel_id=message.channel.id)
            historical_context = await cognition.summarize(similar_messages)

            # Catch empty messages
            if not user_message:
                user_message = bot.user.name
            
            # Preparing API request paramters
            gpt_response  = ''
            short_history = await ShortTermMemory.read(id=message.channel.id)
            nametag       = f'{message.author.display_name} said:'

            primary       = True # Is it the primary message?
            async for packet in cognition.chat_link(
                                    message=user_message,
                                    nametag=nametag,
                                    historical_context=historical_context,
                                    short_history=short_history):
                try:
                    if primary:
                        await message.reply(packet) # Send packet as a reply
                        primary = False
                    else:
                        await message.channel.send(packet) # Send as regular message
                    
                    gpt_response += packet # Append to full message

                # Error handling
                except Exception as exception:
                    try:
                        await message.channel.send(
                            f"## `Error`\n```vbnet\n{handle_exception(exception)}\n```")
                    except Exception as ex:
                        title = f"## Unexpected `Error`\n"
                        no_md = f"```md\n{discord.utils.escape_markdown(user_message)}\n```\n"
                        error = f"```vbnet\n{handle_exception(ex)}\n```"
                        await message.author.send(f"{title}{no_md}{error}")

    '''Updating ShortTermMemory.'''
    if message.author != bot.user:
        # Pushes user package
        package_user = {
            'guild.id'   : message.guild.id,
            'channel.id' : message.channel.id,
            'message.id' : message.id,
            'timestamp'  : message.created_at,
            'author'     : {
                'id'     : message.author.id,
                'name'   : message.author.display_name,
                            },
            'message'    : user_message,
        }
        await ShortTermMemory.add(package=package_user)
    
    # Pushes bot package
    if bot.user in message.mentions:
        # Ignore own messages
        if message.author == bot.user:
            return
        
        package_bot  = {
            'guild.id'   : message.guild.id,
            'channel.id' : message.channel.id,
            'message.id' : message.id,
            'timestamp'  : message.created_at,
            'author'     : {
                'id'     : bot.user.id,
                'name'   : bot.user.name
                            },
            'message'    : gpt_response,
        }
        await ShortTermMemory.add(package=package_bot)

    # utility.clear()
    # print('\n'.join(message['content'] for message in await ShortTermMemory.read(message.channel.id)))

'''
Run the bot
'''
try:
    utility.clear()
    bot.run(constants.DISCORD_BOT_TOKEN)
except Exception as exception:
    print(
        f">> INITIALIZATION ERROR <<\n{handle_exception(exception)}"
    )
    sys.exit()