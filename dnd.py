import discord
import os
from discord.ext import commands
import random
import config
import asyncio

client = commands.Bot(command_prefix='!')
dice_list = ["D4", "D6", "D8", "D10", "D12", "D20", "D100"]



@client.event
async def on_ready():  # When the bot is ready will post these things
    print('Logged in as')
    print(client.user.name)
    # print(client.user.id)
    print('DND Online')
    print('------')


class Dnd(commands.Cog):
    """All DND Commands"""

    @commands.command(name='roll', help='Rolls a dice')
    async def roll(self, ctx, *, args):
        """Rolls a dice"""
        if args.upper() in dice_list:
            await ctx.send(f'You rolled a {args.upper()} and got {random.randint(1, int(args[1:]))}')
        else:
            await ctx.send('Please enter a valid dice')
            await ctx.send('Valid dice are: D4, D6, D8, D10, D12, D20, D100')


client.add_cog(Dnd(client))
client.run(config.token)
