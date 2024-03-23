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


@bot.command()
async def s(ctx):
  message_queue = deque([])
  message = ctx.message.content[2:]
  usernick = ctx.message.author.display_name
  message = usernick + " says " + message

  try:
    vc = ctx.message.guild.voice_client
    if not vc.is_playing():
      tts = gTTS(message, lang='vi', slow=False)
      f = TemporaryFile()
      tts.write_to_fp(f)
      f.seek(0)
      vc.play(discord.FFmpegPCMAudio(f, pipe=True))
    else:
      message_queue.append(message)
      while vc.is_playing():
        await asyncio.sleep(0.1)
      tts = gTTS(message_queue.popleft(), lang='vi', slow=False)
      f = TemporaryFile()
      tts.write_to_fp(f)
      f.seek(0)
      vc.play(discord.FFmpegPCMAudio(f, pipe=True))
  except (TypeError, AttributeError):
    try:
      tts = gTTS(message, lang='vi', slow=False)
      f = TemporaryFile()
      tts.write_to_fp(f)
      f.seek(0)
      channel = ctx.message.author.voice.channel
      vc = await channel.connect()
      vc.play(discord.FFmpegPCMAudio(f, pipe=True))
    except (AttributeError, TypeError):
      await ctx.send("I'm not in a voice channel and neither are you!")
    return
  f.close()

# Run the bot
keepalive()
bot.run(TOKEN, reconnect=True)