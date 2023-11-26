'''
voice
~~~~~
Centralized voice management.
'''
'''
██╗   ██╗ ██████╗ ██╗ ██████╗███████╗
██║   ██║██╔═══██╗██║██╔════╝██╔════╝
██║   ██║██║   ██║██║██║     █████╗  
╚██╗ ██╔╝██║   ██║██║██║     ██╔══╝  
 ╚████╔╝ ╚██████╔╝██║╚██████╗███████╗
  ╚═══╝   ╚═════╝ ╚═╝ ╚═════╝╚══════╝                                                                                               
'''

# Import libraries
import discord
import wavelink
from src.core import constants

async def connect_nodes(bot=discord.Bot()):
  """
  Create and connect to the Lavalink server.
  """
  # Create a node
  node = wavelink.Node(
    uri      = f'https://{constants.LAVALINK_HOST}:{constants.LAVALINK_PORT}',
    password = constants.LAVALINK
  )

  # Connect to node
  await wavelink.NodePool.connect(
    client = bot,
    nodes  = [node]
    )
  
async def play(ctx, search: str):
  """
  Plays audio
  """

  vc = ctx.voice_client # define our voice client

  if not vc: # check if the bot is not in a voice channel
    vc = await ctx.author.voice.channel.connect(cls=wavelink.Player) # connect to the voice channel

  if ctx.author.voice.channel.id != vc.channel.id: # check if the bot is not in the voice channel
    return await ctx.respond("You must be in the same voice channel as the bot.") # return an error message

  songs = await wavelink.YouTubeTrack.search(search) # search for the song
  song = songs[0] if songs else None

  if not song: # check if the song is not found
    return await ctx.respond("No song found.") # return an error message

  await vc.play(song) # play the song
  await ctx.respond(f"Now playing: `{song.title}`")




    
    


