'''
voice cog
~~~~~~~~~
Centralized voice management cog.
'''
'''
██╗   ██╗ ██████╗ ██╗ ██████╗███████╗  
██║   ██║██╔═══██╗██║██╔════╝██╔════╝    ____    ____     ____  
██║   ██║██║   ██║██║██║     █████╗    _/ ___\  /  _ \   / ___\ 
╚██╗ ██╔╝██║   ██║██║██║     ██╔══╝    \  \___ (  <_> ) / /_/  >
 ╚████╔╝ ╚██████╔╝██║╚██████╗███████╗   \___  > \____/  \___  / 
  ╚═══╝   ╚═════╝ ╚═╝ ╚═════╝╚══════╝       \/         /_____/                                                                                                 
'''

# Import libraries
import discord
from discord.ext import commands, tasks
import asyncio

# Import modules
from src.core import constants
from src.voice import tts

class Voice(commands.Cog):
    """
    Voice Cog
    ~~~~~~~~~
    Maintains all VC methods in a modular way.
    """
    
    def __init__(self, bot: discord.Bot):
        """
        Initialize the class.
        """
        self.bot = bot
        
        # Idle loop
        self.idle_loop.start()  
    

    '''
    VC Methods
    '''

    async def verify(self, ctx) -> bool:
        """
        Verifies if the ctx is eligible.
        """
        # 1. Reject non-guild requests (DMs)
        if ctx.guild is None:
            await ctx.respond('i can only vc in servers', ephemeral=True)
            return False

        # 2. Reject if not in VC
        elif ctx.author.voice is None:
            await ctx.respond('you have to join vc first', ephemeral=True)
            return False
        
        # 3. Reject if already in VC
        elif ctx.guild.voice_client is not None:
            await ctx.respond('im already in vc', ephemeral=True)
            return False
                    
        # Passed!
        else:
            return True

    async def connect(self, ctx):
        """
        Connects to voice channel.
        """
        try:
            # Run verification
            if await self.verify(ctx):

                # Obtain channel
                channel = ctx.author.voice.channel
                # Connect to channel
                await channel.connect()
                await ctx.respond('ok ready now', ephemeral=True)
            
        except Exception as e:
            await ctx.respond(f"i think it broke: `{e}`", ephemeral=True)


    @discord.slash_command()
    async def vc(self, ctx):
        """
        Start a voice call.
        """
        await self.connect(ctx)


    '''
    Utility Methods
    '''

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """
        Handles change of voice state.
        Ensures voice channel connections are robust.
        """
        # Check if member was bot
        if member == self.bot.user:
            
            # If change was a *connect*
            if after.channel is not None: # changed VC/joined VC
                await self.handle_connect(guild=member.guild)

            # If change was a *disconnect*
            if before.channel is not None and after.channel is None: # no longer in VC
                await self.handle_disconnect(guild=member.guild)
    
    async def handle_connect(self, guild):
        """
        Handles state change: connect.
        """
        pass # nothing here yet!

    async def handle_disconnect(self, guild):
        """
        Handles state change: disconnect.
        """
        # 1. Cleanup zombie channels if required
        if guild.voice_client is not None:
            try:
                await self.cleanup(guild)
            except Exception as e:
                print(f'Could not cleanup channel: {e}')
    
    async def cleanup(self, guild):
        """
        Cleanup zombie voice channel connections.
        """
        voice_client = guild.voice_client

        # First disconnect the client from zombie channel
        await voice_client.disconnect()

        # Then cleanup() zombie channel
        voice_client.cleanup()

    '''
    Loop Methods
    '''

    @tasks.loop(seconds=constants.VOICE_IDLE)
    async def idle_loop(self):
        """
        Check all voice channels the bot is in and disconnect if alone.
        """
        for vc in self.bot.voice_clients:
            # If connected and alone
            if vc.is_connected() and len(vc.channel.members) == 1:
                # Wait for the grace period
                await asyncio.sleep(constants.VOICE_IDLE)  
                # Recheck to see if still alone
                if len(vc.channel.members) == 1:  
                    await vc.disconnect() # Disconnect

    @idle_loop.before_loop
    async def before_idle_loop(self):
        await self.bot.wait_until_ready()

    def cog_unload(self):
        """
        Cancel all idle loops when the cog is unloaded
        """
        self.idle_loop.cancel()


