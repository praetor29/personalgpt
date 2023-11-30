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
from src.voice.vad import VADSink

class Voice(commands.Cog):
    """
    Voice Cog
    ~~~~~~~~~
    Maintains all VC methods in a modular way.
    """
    
    def __init__(self, bot: discord.Bot):
            """
            Initialize the Voice class.

            Args:
                bot (discord.Bot): The Discord bot instance.

            Attributes:
                bot (discord.Bot): The Discord bot instance.
                idle_loop (discord.ext.tasks.Loop): The idle loop task.
                vad (webrtcvad.Vad): The VAD (Voice Activity Detector) instance.
            """
            self.bot = bot
            
            # Idle loop
            self.idle_loop.start()

            # VAD instance
            self.vad_sink = VADSink()

    '''
    VC Methods
    '''

    async def verify(self, ctx) -> bool:
            """
            Verifies if the ctx is eligible.

            Parameters:
            - ctx: The context object representing the command invocation.

            Returns:
            - bool: True if the context is eligible, False otherwise.
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
            Connects to the voice channel and starts recording.

            Parameters:
            - ctx: The context object representing the command invocation.

            Returns:
            None
            """
            try:
                # Run verification
                if await self.verify(ctx):

                    # Obtain channel
                    channel = ctx.author.voice.channel
                    # Connect to channel
                    await channel.connect()
                    
                    await ctx.respond('ok ready now', ephemeral=True)

                    # Start the recording task
                    await self.record(ctx)
                
            except Exception as e:
                await ctx.respond(f"i think it broke: `{e}`", ephemeral=True)
    
    async def record(self, ctx):
            """
            Records audio from voice channel.

            Parameters:
            - ctx: The context object representing the command invocation.

            Returns:
            None
            """
            # Obtain voice client
            voice_client = ctx.guild.voice_client
            
            try:
                # Start recording
                voice_client.start_recording(
                    self.vad_sink,  # VADSink() instance
                    self.once_done,  # Calls dummy function once recording is done
                    None
                )
                asyncio.create_task(self.vad_sink.vad_loop())

            except Exception as e:
                await ctx.respond(f"i think it broke: `{e}`", ephemeral=True)

    @discord.slash_command()
    async def vc(self, ctx):
        """
        Start a voice call.
        """
        await self.connect(ctx)

    
    async def once_done(self, sink: discord.sinks, channel: discord.TextChannel, *args):
        """
        Called once the recording is done.

        Receives inputs, does nothing.
        """
        pass

    '''
    Listener Methods
    '''

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """
        Handles change of voice state.
        Ensures voice channel connections are robust.

        Parameters:
        - member: The member whose voice state changed.
        - before: The voice state before the change.
        - after: The voice state after the change.
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

        Parameters:
        - guild: The guild object representing the connected guild.

        Returns:
        None
        """
        voice_client = guild.voice_client
        pass

    async def handle_disconnect(self, guild):
            """
            Handles state change: disconnect.

            1. Cleanup zombie channels
            2. Stop recording

            Args:
                guild (discord.Guild): The guild object representing the server.
            """
            voice_client = guild.voice_client

            if voice_client is not None:
                # 1. Cleanup zombie channels if required
                try:
                    await self.cleanup(guild)
                except Exception as e:
                    print(f'Could not cleanup channel: {e}')

                # 2. Stop recording
                voice_client.stop_recording()

    async def cleanup(self, guild):
        """
        Cleanup zombie voice channel connections.

        Parameters:
        - guild: The guild object representing the server.
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
        """
        This method is called before the idle loop starts.
        It waits until the bot is ready before proceeding.
        """
        await self.bot.wait_until_ready()

    def cog_unload(self):
        """
        Cancel all idle loops when the cog is unloaded
        """
        self.idle_loop.cancel()
