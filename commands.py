import discord
import os
from discord.ext import commands
import config
import logging

intents = discord.Intents.all()
intents.members = True

client = commands.Bot(command_prefix='!', intents=intents)
logging.basicConfig(level=logging.INFO)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    # print(client.user.id)
    print('Commands Online')
    print('------')


@client.event
async def on_member_join(self, member):
    guild = member.guild
    if guild.system_channel is not None:
        to_send = f"Welcome {member.mention} to {guild.name}!"
        await guild.system_channel.send(to_send)


@client.command()
async def hello(ctx, *args):
    for arg in args:
        await ctx.send(arg)

    print(ctx.author)
    print(ctx.message)
    print(ctx.guild)
    print("Hello Command Was Run")


@client.command()
async def server(ctx):
    avatar = ctx.message.author.avatar
    embed = discord.Embed(title=f"{ctx.guild.name} Info", description="Information of this Server",
                          color=discord.Colour.blue())
    embed.add_field(name='🆔Server ID', value=f"{ctx.guild.id}", inline=True)
    embed.add_field(name='📆Created On', value=ctx.guild.created_at.strftime("%b %d %Y"), inline=True)
    embed.add_field(name='👑Owner', value=f"{ctx.guild.owner}", inline=True)
    embed.add_field(name='👥Members', value=f'{ctx.guild.member_count} Members', inline=True)
    embed.add_field(name='💬Channels',
                    value=f'{len(ctx.guild.text_channels)} Text | {len(ctx.guild.voice_channels)} Voice', inline=True)
    embed.add_field(name='🌎Region', value=f'{ctx.guild.region}', inline=True)
    embed.set_thumbnail(url=ctx.guild.icon)
    embed.set_footer(text="⭐ • Duo")
    embed.set_author(name=f'{ctx.author.name}', icon_url=avatar)
    await ctx.send(embed=embed)
    print("server Command Was Run")


@client.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(client.latency * 1000)}ms')
    print("Ping Command Was Run")


@client.command()
async def joined(ctx, member: discord.Member):
    """Says when a member joined."""
    await ctx.send(f"{member.name} joined on {member.joined_at}")


@client.command(name='purge', help='purges chat', aliases=['Purge'])
async def purge(ctx, arg: int):
    await ctx.channel.purge(limit=arg)
    print("Purge Command Was Run")


client.run(config.token)
