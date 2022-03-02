import discord
import os
from discord.ext import commands
import config
from discord import ClientException
from discord.ext import commands
from pretty_help import DefaultMenu, PrettyHelp
from asyncio import sleep
import random
import pymongo
from pymongo import MongoClient
import config
import datetime

# -----------------------------------------------------------------------------------------------------------------------

bot = commands.Bot(command_prefix='!', description='Economy Bot')

slashcom = discord.slash_command()
cluster = MongoClient(
    config.database)
db = cluster["DiscordEconomy"]

econposts = db.economy  # collection for Updating Economy Posts
crimeprompt = db.crimeprompts  # collection for Crime Prompts#


@bot.event
async def on_ready():  # When the bot is ready will post these things
    print('Logged in as')
    print(bot.user.name)
    # print(client.user.id)
    print('Economy Online')
    print('------')


# nav = Navigation("◀️", "▶️", "❌")
menu = DefaultMenu(page_left="◀️", page_right="▶️", remove="❌")
end_note = "Created by: @Streamz#1631"
bot.help_command = PrettyHelp(menu=menu, color=discord.colour.Color.from_rgb(253, 209, 0),
                              ending_note=end_note)  # Race Yellow With Menu


class Economy(commands.Cog):
    """All Economy Commands"""

    @commands.command(
        name="work",
        aliases=["Work"],
        brief="Work and Gain Money",
        help="Use this command to earn money legally",

    )
    async def _work(self, ctx):
        money = random.randint(1, 10)  # Randomly generate an amount of money
        await ctx.send("You worked and earned $" + "{}".format(money))
        try:  # If the user has never had an entry in the database
            balance = {"_id": str(ctx.message.author.id),
                       "Name": str(ctx.message.author.name),
                       "Balance": int(money),
                       "CreatedDate": datetime.datetime.utcnow(),
                       "UpdatedDate": datetime.datetime.utcnow()}
            econposts.insert_one(balance)
            await ctx.send("You now have $" + str(balance["Balance"]))
        except:  # If the user has an entry in the database
            searchbyId = econposts.find_one({"_id": str(ctx.message.author.id)})
            idBalance = searchbyId["Balance"]
            filter = {"_id": str(ctx.message.author.id)}
            newbalance = {"$set": {"Balance": idBalance + money}}
            econposts.update_one(filter, newbalance)
            econposts.update_one(filter, {"$set": {"UpdatedDate": datetime.datetime.utcnow()}})
            NewSearchofID = econposts.find_one({"_id": str(ctx.message.author.id)})
            await ctx.send("You now have $" + str(NewSearchofID["Balance"]))

    @commands.command(
        name="balance",
        aliases=["bank", "money", "bal", "Balance", "Money", "Bal"],
        brief="Check your balance",
        help="Get the total amount of money that is in your balance"
    )
    async def _balance(self, ctx):
        try:
            searchbyId = econposts.find_one({"_id": str(ctx.message.author.id)})  # Search for the user in the database
            idBalance = searchbyId["Balance"]  # Get the balance from the database
            await ctx.send("You have $" + str(idBalance))  # Send the balance to the user
        except:
            balance = 0  # If the user has never had an entry in the database
            await ctx.send(f"{ctx.message.author.mention}'s balance is {balance}")  # Send the balance to the user
            await ctx.send("Try !work or !crime to start earning money")  # Remind the user to work or commit crimes

    @commands.command(
        name="crime",
        aliases=["Crime"],
        brief="Do Crime and Gain Money",
        help="Use this command to earn money illegally"
    )
    async def _crime(self, ctx):
        money = random.randint(20, 50)  # Generate a random amount of money
        promptnum = random.randint(1, 4)  # Generate a random number for the prompt id
        findprompt = crimeprompt.find_one({"_id": str(promptnum)})  # Find the prompt
        await ctx.send(str(findprompt["Prompt"]) + "{}".format(money))  # Send the prompt and the amount of money
        try:  # If the user has never had an entry in the database
            balance = {"_id": str(ctx.message.author.id),
                       "Name": str(ctx.message.author.name),
                       "Balance": int(money),
                       "CreatedDate": datetime.datetime.utcnow(),
                       "UpdatedDate": datetime.datetime.utcnow()}
            econposts.insert_one(balance)
            await ctx.send("You now have $" + str(balance["Balance"]))
        except:  # If the user has an entry in the database
            searchbyId = econposts.find_one({"_id": str(ctx.message.author.id)})
            idBalance = searchbyId["Balance"]
            filter = {"_id": str(ctx.message.author.id)}
            newbalance = {"$set": {"Balance": idBalance + money}}
            econposts.update_one(filter, newbalance)
            econposts.update_one(filter, {"$set": {"UpdatedDate": datetime.datetime.utcnow()}})
            NewSearchofID = econposts.find_one({"_id": str(ctx.message.author.id)})
            await ctx.send("You now have $" + str(NewSearchofID["Balance"]))


@bot.slash_command(guild_ids=[917236140422070283], name="ping", description="Get bot ping")
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')
    print("Ping Command Was Run")


bot.add_cog(Economy(bot))
bot.run(config.token)
