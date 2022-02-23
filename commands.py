import discord
import os
from discord.ext import commands
import config

client = commands.Bot(command_prefix='!')


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    #print(client.user.id)
    print('Commands Online')
    print('------')


@client.command()
async def hello(ctx, *args):
    for arg in args:
        await ctx.send(arg)

    print(ctx.author)
    print(ctx.message)
    print(ctx.guild)
    print("Hello Command Was Run")


@client.command()
async def serverinfo(ctx):
    name = str(ctx.guild.name)
    description = str(ctx.guild.description)

    owner = str(ctx.guild.owner)
    id = str(ctx.guild.id)
    region = str(ctx.guild.region)
    memberCount = str(ctx.guild.member_count)

    icon = str(ctx.guild.icon_url)

    embed = discord.Embed(
        title=name + " Server Information",
        description=description,
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=icon)
    embed.add_field(name="Owner", value=owner, inline=True)
    embed.add_field(name="Server ID", value=id, inline=True)
    embed.add_field(name="Region", value=region, inline=True)
    embed.add_field(name="Member Count", value=memberCount, inline=True)

    await ctx.send(embed=embed)
    print("serverinfo Command Was Run")


@client.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(client.latency * 1000)}ms')
    print("Ping Command Was Run")

@client.command()
async def purge(ctx, arg: int):
    await ctx.channel.purge(limit=arg)
    print("Purge Command Was Run")


client.run(config.token)
