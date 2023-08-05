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
    await bot.change_presence(
        status   = discord.Status.idle,
        activity = discord.Activity(
        type     = discord.ActivityType.listening,
        name     = constants.SONG,
        )
    )
    print(f'Successfully logged in as {bot.user}.')

'''
Bot functioning
'''

# Initialize ShortTermMemory
ShortTermMemory = memory.ShortTermMemory()

@bot.event
async def on_message(message):   

    '''Response loop when mentioned.'''
    if bot.user in message.mentions:
        # Ignore own messages
        if message.author == bot.user:
            return
        
        # Strip prefix
        bot_prefix   = f'<@{bot.user.id}>'
        user_message = message.content.removeprefix(bot_prefix).strip()

        # Catch empty messages
        if not user_message:
            user_message = bot.user.name

        try:
            short_history = await ShortTermMemory.read(id=message.channel.id)
            gpt_response  = await cognition.chat_response(input=user_message,
                                                          short_history=short_history)
        except cognition.openai.error.OpenAIError:
            gpt_response = constants.ERROR_OPENAI
               
        payload = utility.splitter(gpt_response)
        for packet in payload:
            try:
                await message.reply(packet)
            except discord.errors.HTTPException:
                await message.reply(constants.ERROR_OPENAI)

    '''Updating ShortTermMemory.'''
    if message.author != bot.user:
        # Pushes user package
        package_user = {
            'channel.id' : message.channel.id,
            'timestamp'  : utility.current_date(),
            'author'     : {
                'id'     : message.author.id,
                'name'   : message.author.name
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
    
    # print('\n'.join(message['content'] for message in await ShortTermMemory.read(message.channel.id)))



'''
Run the bot
'''
bot.run(constants.DISCORD_BOT_TOKEN)
