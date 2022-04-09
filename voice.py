import discord
import yt_dlp
import os
import asyncio
import config
import logging

from discord import ClientException
from discord.ext import commands
from discord.ext.commands import bot, Bot

intents = discord.Intents.all()
intents.members = True

client = commands.Bot(command_prefix='!', intents=intents)
logging.basicConfig(level=logging.INFO)

playlist = []


@client.event
async def on_ready():  # When the bot is ready will post these things
    print('Logged in as')
    print(client.user.name)
    # print(client.user.id)
    print('Voice Online')
    print('------')


async def play_next(ctx, source):  # Plays the next song in the queue
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if playlist[0] is None:  # If the queue is empty
        playlist.pop()  # Remove the first item in the queue
        pass
    else:
        if len(playlist) >= 1:  # If the queue is not empty
            if voice.is_playing():  # If the bot is playing a song
                voice.stop()  # Stop the music
                await play(ctx, playlist[0])  # Play the next song in the queue: Sends to play function
                print("Playing next song")
                print(playlist[0])
            else:  # If the bot is not playing a song
                await play(ctx, playlist[0])
                print("Playing next song")
                print(playlist[0])


async def queuecheck(ctx):  # Completely Useless RN
    if len(playlist) >= 1:
        await ctx.send("The queue is currently empty.")


@client.command()
async def join(ctx):  # Joins the voice channel
    connected = ctx.author.voice
    if connected:
        await connected.channel.connect()
        print("Connected to \"" + connected.channel.name + "\""" voice channel")
    else:
        await ctx.send("You are not connected to a Voice Channel.")


@client.command(name='play', help='Play a song', aliases=['plays', 'p'])
async def play(ctx, url: str):  # Plays a song
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    song_there = os.path.isfile("song.mp3")
    voice.stop
    try:  # determines if song file is in directory
        if song_there:
            os.remove("song.mp3")
    except PermissionError:
        await ctx.send("Wait for the current playing music to end or use the 'stop' command")
        return
    except ClientException:
        return

    try:
        connected = ctx.author.voice
        await connected.channel.connect()  # Connects to the voice channel
        print("Connected to \"" + connected.channel.name + "\""" voice channel")
    except discord.ClientException:
        pass
    ydl_opts = {  # Youtube Download Options for song
        'format': 'bestaudio/best',
        "quiet": True,
        "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
        "restrict-filenames": True,
        "nocheckcertificate": True,
        "ignore-errors": False,
        "default-search": "auto",
        "source-address": "0.0.0.0",
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    try:  # FOR QUEUE: IF there is a song from the queue still in here, removes it
        playlist.pop()
    except IndexError:
        pass
    playlist.append(url)
    for i in playlist:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(playlist[0])
        for file in os.listdir("./"):
            if file.endswith(".mp3"):
                os.rename(file, "song.mp3")
        await ctx.send("Playing: " + playlist[0])
        voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: play_next(ctx, playlist[0]))
        voice.pause()  # Pauses to sync audio, basically pauses 1 second to attempt program to catch up to audio
        await asyncio.sleep(1)
        voice.resume()
        playlist.pop(0)


@client.command()
async def leave(ctx):  # Leaves the voice channel
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_connected():
        await voice.disconnect()
        voice.stop()
        await asyncio.sleep(2)
        os.remove("song.mp3")  # Deletes the song.mp3 file
    else:
        await ctx.send("The bot is not connected to a voice channel.")


@client.command()
async def pause(ctx):  # Pauses the music
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
        print("Paused")
        ctx.send("Music Paused")
    else:
        await ctx.send("Currently no audio is playing.")


@client.command()
async def resume(ctx):  # Resumes the music
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
        print("Resumed")
        ctx.send("Music Resumed")
    else:
        await ctx.send("The audio is not paused.")


@client.command()
async def stop(ctx):  # Stops the music and clears the queue
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    voice.stop()
    await clear(ctx)
    ctx.send("Music Stopped and Queue Cleared")


@client.command()
async def add(ctx, url: str):  # Adds a song to the queue
    playlist.append(url)
    await ctx.send("Added to playlist")


@client.command()
async def clear(ctx):  # Clears the queue
    playlist.clear()
    await ctx.send("Playlist cleared")


@client.command()
async def skip(ctx):  # Skips the current song
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    print(playlist[0])
    if voice.is_playing():  # Checks if there is a song playing
        voice.stop()
        await play_next(ctx, playlist[0])
    if not voice.is_playing():  # Checks if there is a song playing
        voice.stop()
        await ctx.send("Currently no audio is playing.")
        await ctx.send("Attempting to skip song NOW...")
        await play_next(ctx, playlist[0])
        # playlist.pop(0)

    else:  # useless rn
        await ctx.send("Currently no audio is playing.")
        await ctx.send("Attempting to skip song...")
        await ctx.invoke(play(ctx.get_command('play'), playlist[0]))


@play.before_invoke
async def ensure_voice(ctx):  # Checks if the bot is connected to a voice channel
    if ctx.voice_client is None:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send("You are not connected to a voice channel.")
            raise commands.CommandError("Author not connected to a voice channel.")
    elif ctx.voice_client.is_playing():
        ctx.voice_client.stop()


@client.command(
    name='queue',
    description='Displays Queue.',
    aliases=['q'],
)
async def queue(ctx):  # Displays the queue
    await ctx.send(playlist)


client.run(config.token)
