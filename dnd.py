from time import sleep
import re
import discord
import os
from discord.ext import commands
import random

from pymongo.errors import DuplicateKeyError

import config
import asyncio
import pymongo
from pymongo import MongoClient
import config
import datetime

client = commands.Bot(command_prefix='!')
dice_list = ["D4", "D6", "D8", "D10", "D12", "D20", "D100"]
# --------------------------
cluster = MongoClient(
    config.database)
db = cluster["Dnd"]
characters = db["Characters"]


# -------------------------

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
        if args is None: # if no args are given
            await ctx.send('Please enter a name for your character')
            await ctx.send('Example: !create character name')
        else: # if args are given
            if args.upper() == 'CHARACTER' or args.upper() == 'CHAR': # if args are character
                await ctx.send('Please enter a name for your character')
                await ctx.send('Example: !create character name')
                sleep(1)
                character_name = await client.wait_for('message', timeout=60.0)
                sleep(1)
                await ctx.send('Please enter a class for your character')
                character_class = await client.wait_for('message', timeout=60.0)
                await ctx.send(f'You created a new character named {character_name.content.capitalize()} '
                               f'and class is {character_class.content.capitalize()}')
                try:  # If the user has never had an entry in the database
                    characterload = {"_id": str(ctx.message.author.id),
                                     "DiscordName": str(ctx.message.author.name),
                                     "CharacterNum": int(1),
                                     "CharacterName": str(character_name.content.capitalize()),
                                     "CharacterClass": str(character_class.content.capitalize()),
                                     # "CharacterLevel": int(1),
                                     "CreatedDate": datetime.datetime.utcnow(),
                                     "UpdatedDate": datetime.datetime.utcnow()}
                    characters.insert_one(characterload)
                except:  # If the user has had an entry in the database
                    await ctx.send('You already have a character'
                                   '\nYou can only have 3 characters')
                    numofChars = characters.count_documents({"_id": {"$regex": str(ctx.message.author.id)}}) # Counts the number of characters
                    print(numofChars)
                    await ctx.send('You currently have ' + str(numofChars) + ' characters')
                    await ctx.send('Would you like this new character to be saved?')
                    sleep(1)
                    create_another = await client.wait_for('message', timeout=60.0)
                    if create_another.content.upper() == 'YES':
                        await another_char(ctx, 'YES', character_name.content.capitalize(),
                                           character_class.content.capitalize())
                        print('invoked')
                    else:
                        await ctx.send("You said No")
                        await ctx.send("Goodbye")
            else:  # If the user has entered a name for their character
                await ctx.send('Please enter a class for your character')

    @commands.command(name='delete', help='Deletes a character')
    async def delete(self, ctx, *, args): # Deletes a character
        """Deletes a character"""
        if args.upper() == 'CHARACTER' or args.upper() == 'CHAR':
            await ctx.send('Please enter a name for your character')
            await ctx.send('Example: !delete character name')
            sleep(1)
            character_name = await client.wait_for('message', timeout=60.0)
            try:
                characters.delete_one({"CharacterName": character_name.content.capitalize()})
                await ctx.send('Character deleted')
            except:
                await ctx.send('Character not found')
                await ctx.send("use !list to see all your characters")
        else:
            await ctx.send('Please use !delete character')

    @commands.command(name='list', help='Lists all characters')
    async def list(self, ctx): # Lists all characters
        """Lists all characters"""
        numofChars = characters.count_documents({"_id": {"$regex": str(ctx.message.author.id)}})
        if numofChars == 0:
            await ctx.send('You have no characters')
        else:
            await ctx.send('You currently have ' + str(numofChars) + ' characters')
            for x in characters.find({"_id": {"$regex": str(ctx.message.author.id)}}):
                await ctx.send("Character #" + str(x['CharacterNum']))
                await ctx.send("Character Name: " + x['CharacterName'])
                await ctx.send("Character Class: " + x['CharacterClass'])
                await ctx.send("Created at: " + str(x['CreatedDate'])[0:15])
                await ctx.send("---------------------------------")


async def another_char(ctx, args, character_name, character_class): # Creates another character 2nd or 3rd
    # create_another = await client.wait_for('message', timeout=60.0)
    if args.upper() == 'YES':
        numofChars = characters.count_documents({"_id": {"$regex": str(ctx.message.author.id)}})
        print(numofChars)
        if numofChars == 3:
            await ctx.send('You already have 3 characters')
            await ctx.send('Would you like to delete a character?')
        else:
            await ctx.send(f'You created a new character named {character_name.capitalize()} '
                           f'and class is {character_class.capitalize()}')
            try:  # If the user has never had an entry in the database
                characterload = {"_id": str(ctx.message.author.id) + "#" + str(numofChars),
                                 "DiscordName": str(ctx.message.author.name),
                                 "CharacterNum": int(int(numofChars) + 1),
                                 "CharacterName": str(character_name.capitalize()),
                                 "CharacterClass": str(character_class.capitalize()),
                                 # "CharacterLevel": int(1),
                                 "CreatedDate": datetime.datetime.utcnow(),
                                 "UpdatedDate": datetime.datetime.utcnow()}
                characters.insert_one(characterload)
            except:  # If the user has had an entry in the database
                await ctx.send('You already have a character'
                               '\nYou can only have 3 characters')
                await ctx.send('Would you like to create another character?')
                create_another = await client.wait_for('message', timeout=60.0)
                if create_another.content.upper() == 'YES':
                    await another_char(ctx, 'YES', character_name.capitalize(), character_class.capitalize())
                else:
                    await ctx.send("You said No")


async def update_character(ctx, character_name, character_class):
    characterload = {"_id": str(ctx.message.author.id),
                     "DiscordName": str(ctx.message.author.name),
                     "CharacterNum": int(1),
                     "CharacterName": str(character_name),
                     "CharacterClass": str(character_class),
                     # "CharacterLevel": int(1),
                     "CreatedDate": datetime.datetime.utcnow(),
                     "UpdatedDate": datetime.datetime.utcnow()}
    characters.insert_one(characterload)



client.add_cog(Dnd(client))
client.run(config.token)
