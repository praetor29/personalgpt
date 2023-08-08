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
    LongTermMemory  = memory.LongTermMemory(db_path=constants.MEMORY_DB_PATH)
    print(f">> Initializing '{constants.MEMORY_DB_PATH}' SQLite database...")
    await LongTermMemory.initialize_db() # Create memory.db and table (if not exist)

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
        status   = discord.Status.idle,
        activity = discord.Activity(
        type     = discord.ActivityType.listening,
        name     = constants.SONG,
        )
    )
    # Login message
    login = f'Successfully logged in as {bot.user}.'
    print('\n+-' + '-' * len(login) + '-+'  )
    print(f'| {login} |')
    print(  '+-' + '-' * len(login) + '-+\n')

'''
Bot functioning
'''
@bot.event
async def on_message(message):   

    '''Response loop when mentioned.'''
    if bot.user in message.mentions:
        # Ignore own messages
        if message.author == bot.user:
            return

        # Prepare user_message for API call
        bot_prefix     = f'<@{bot.user.id}>'
        user_message   = message.content.removeprefix(bot_prefix).strip()

        # Catch empty messages
        if not user_message:
            user_message = bot.user.name
        
        gpt_response  = ''
        short_history = await ShortTermMemory.read(id=message.channel.id)
        system_message = f'{utility.current_date()} | {message.author.display_name}:'

        primary       = True # Is it the primary message?
        async for packet in cognition.chat_link(user_message  =user_message,
                                                system_message=system_message,
                                                short_history =short_history):
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
            'channel.id' : message.channel.id,
            'timestamp'  : utility.current_date(),
            'author'     : {
                'id'     : message.author.id,
                'name'   : message.author.display_name,
                            },
            'message'    : message.clean_content,
        }
        await ShortTermMemory.add(package=package_user)
    
    # Pushes bot package
    if bot.user in message.mentions:
        # Ignore own messages
        if message.author == bot.user:
            return
        
        package_bot  = {
            'channel.id' : message.channel.id,
            'timestamp'  : utility.current_date(),
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