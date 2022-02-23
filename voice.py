import discord
import yt_dlp
import os
import asyncio
import config

from discord import ClientException
from discord.ext import commands
from discord.ext.commands import bot, Bot

client = commands.Bot(command_prefix='!')

playlist = []


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    # print(client.user.id)
    print('Voice Online')
    print('------')


def play_next(ctx, source):
    if len(playlist) >= 1:
        del playlist[0]
        voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
        voice.play(discord.FFmpegPCMAudio(source=source), after=lambda e: play_next(ctx, source))


@client.command()
async def join(ctx):
    connected = ctx.author.voice
    if connected:
        await connected.channel.connect()
        print("Connected to \"" + connected.channel.name + "\""" voice channel")
    else:
        await ctx.send("You are not connected to a Voice Channel.")


@client.command(name='play', help='Play a song', aliases=['plays', 'p'])
async def play(ctx, url: str):
    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
    except PermissionError:
        await ctx.send("Wait for the current playing music to end or use the 'stop' command")
        return
    except ClientException:
        return

    try:
        connected = ctx.author.voice
        await connected.channel.connect()
        print("Connected to \"" + connected.channel.name + "\""" voice channel")
    except discord.ClientException:
        pass
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    ydl_opts = {
        'format': 'bestaudio/best',
        "quiet": True,
        "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
        "restrictfilenames": True,
        "nocheckcertificate": True,
        "ignoreerrors": False,
        "no_warnings": True,
        "default_search": "auto",
        "source_address": "0.0.0.0",
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    playlist.append(url)
    for i in playlist:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(playlist)
        for file in os.listdir("./"):
            if file.endswith(".mp3"):
                os.rename(file, "song.mp3")
        await ctx.send("Playing: " + playlist[0])
        playlist.pop(0)
        voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: play_next(ctx, playlist[0]))
        voice.pause()  # Pauses to sync audio, basically no more quick 2-3 seconds of audio
        await asyncio.sleep(3)
        voice.resume()


@client.command()
async def leave(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_connected():
        await voice.disconnect()
        playlist.clear()
        os.remove("song.mp3")  # Deletes the song.mp3 file
    else:
        await ctx.send("The bot is not connected to a voice channel.")


@client.command()
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
        print("Paused")
    else:
        await ctx.send("Currently no audio is playing.")


@client.command()
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
        print("Resumed")
    else:
        await ctx.send("The audio is not paused.")


@client.command()
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    voice.stop()


@client.command()
async def add(ctx, url: str):
    playlist.append(url)
    await ctx.send("Added to playlist")


@client.command()
async def clear(ctx):
    playlist.clear()
    await ctx.send("Playlist cleared")


@client.command()
async def skip(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.stop()
        await play(ctx, playlist[0])
    if not voice.is_playing():
        await ctx.send("Currently no audio is playing.")
        await ctx.send("Attempting to skip song NOW...")
        await ctx.invoke(Bot.get_command('play'), playlist[0])
    else:
        await ctx.send("Currently no audio is playing.")
        await ctx.send("Attempting to skip song...")
        await ctx.invoke(play(ctx.get_command('play'), playlist[0]))


@play.before_invoke
async def ensure_voice(ctx):
    if ctx.voice_client is None:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send("You are not connected to a voice channel.")
            raise commands.CommandError("Author not connected to a voice channel.")
    elif ctx.voice_client.is_playing():
        ctx.voice_client.stop()


@client.command()
async def queue(ctx):
    await ctx.send(playlist)


client.run(config.token)
