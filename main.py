# Library
import os
from keepalive import keepalive
import nacl
import discord
import asyncio
from discord.ext import commands
import logging
import datetime
from tempfile import TemporaryFile
from gtts import gTTS
from collections import deque
import ffmpeg
from io import BytesIO

# Setting up logging
logging.basicConfig(filename='bot.log', level=logging.INFO)

TOKEN = os.environ['TOKEN']

# Define the intents your bot will use
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True
intents.members = True
intents.messages = True

# Initialize the bot instance and use a blank prefix:
bot = commands.Bot(command_prefix="", intents=intents)


@bot.event
async def on_ready():
  logging.info(f'{bot.user} has connected to Discord')


# Welcome new member
# Channel ID
# welcome_channel = 1210574029560352768


@bot.event
async def on_member_join(member):
  channel = bot.get_channel(welcome_channel)
  embed = discord.Embed(
      description=f'Hello {member.mention}, welcome to the {member.guild}!',
      color=0xff55ff,
      timestamp=datetime.datetime.now())
  role = discord.utils.get(member.guild.roles, name='Member')
  await member.add_roles(role)
  await channel.send(embed=embed)
  logging.info(f'Member {member.name} has joined the server')


# Invite bot to voice channel
@bot.command(pass_context=True)
async def join(ctx):
  try:
    voice_client = ctx.voice_client
    user_channel = ctx.author.voice.channel

    if voice_client:
      bot_channel = voice_client.channel
      if user_channel == bot_channel:
        logging.info(f'{bot.user} already in your voice channel.')
      else:
        await voice_client.move_to(user_channel)
    elif ctx.author.voice:
      channel = user_channel
      await channel.connect()
    else:
      await ctx.send(
          "You are not in a voice channel. You must be in a voice channel to run this command!"
      )
  except Exception as e:
    logging.error(f"An error occurred: {e}")


# Kick the bot out of the voice channel
@bot.command(pass_context=True)
async def leave(ctx):
  try:
    voice_client = ctx.voice_client
    if voice_client:
      bot_channel = voice_client.channel
      user_channel = ctx.author.voice.channel

      if user_channel and bot_channel == user_channel:
        await voice_client.disconnect(force=True)
        logging.info(f'{bot.user} left the voice channel')
      else:
        await ctx.send("You are not in the same voice channel as the bot.")
    else:
      await ctx.send("I'm not in a voice channel.")
  except Exception as e:
    logging.error(f"An error occurred: {e}")


@bot.command()
async def stop(ctx):  # just an alias for leave
  await leave(ctx)


# Initialize the queue to store messages to be spoken
message_queue = deque([])


# Text to Speech feature
@bot.command()
async def s(ctx, *arg):
  user = ctx.message.author

  if user.voice is None:
    await ctx.send("You need to be in a voice channel to run this command!")
    return

  voice_channel = user.voice.channel
  try:
    vc = await voice_channel.connect()
  except discord.errors.ClientException:
    vc = ctx.voice_client

  # If the bot is already playing, add the message to the queue
  if vc.is_playing():
    message_queue.append(" ".join(arg))
    return

  message_queue.append(" ".join(arg))

  while message_queue:
    text = message_queue.popleft()

    tts = gTTS(text=text, lang='vi', slow=False)
    tts_bytes_io = BytesIO()
    tts.write_to_fp(tts_bytes_io)
    tts_bytes_io.seek(0)

    # Start playing the audio
    vc.play(discord.FFmpegPCMAudio(tts_bytes_io, pipe=True),
            after=lambda e: cleanup_temp_file(tts_bytes_io))
    await asyncio.sleep(
        1)  # Wait for a short duration before playing the next message


# Function to clean up the temporary audio file
async def cleanup_temp_file(tts_bytes_io):
  try:
    tts_bytes_io.close()
  except Exception as e:
    logging.info(f"Error closing BytesIO object: {e}")


# Run the bot
keepalive()
bot.run(TOKEN, reconnect=True)
