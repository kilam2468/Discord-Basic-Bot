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

    # dnd character commands
    @commands.command(name='create', help='Creates a new character')
    async def create(self, ctx, *, args):
        """Creates a new character"""
        if args is None:
            await ctx.send('Please enter a name for your character')
            await ctx.send('Example: !create character name')
        else:
            if args.upper() == 'CHARACTER':
                await ctx.send('Please enter a name for your character')
                await ctx.send('Example: !create character name')
                character_name = await client.wait_for('message', timeout=60.0)
                await ctx.send('Please enter a class for your character')
                character_class = await client.wait_for('message', timeout=60.0)
                await ctx.send(f'You created a new character named {character_name.content.capitalize()} '
                               f'and class is {character_class.content.capitalize()}')
            else:
                await ctx.send(f'You created a new character named {args}')
                character_name = args
                await ctx.send('Please enter a class for your character')
                character_class = await client.wait_for('message', timeout=60.0)
                await ctx.send(f'You created a new character named {character_name} '
                               f'and class is {character_class.content}')

    @commands.command(name='delete', help='Deletes a character')
    async def delete(self, ctx, *, args):
        """Deletes a character"""
        if args.upper() == 'CHARACTER':
            await ctx.send('Please enter a name for your character')
            await ctx.send('Example: !delete character name')


client.add_cog(Dnd(client))
client.run(config.token)
