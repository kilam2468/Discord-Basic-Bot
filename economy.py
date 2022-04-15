import asyncio

import discord
import os
import discord
import os
from discord.ext import commands
import config
from discord import ClientException
from discord.ext import commands
from asyncio import sleep
import random
import pymongo
from pymongo import MongoClient
import config
import datetime
import logging

intents = discord.Intents.all()
intents.members = True

# -----------------------------------------------------------------------------------------------------------------------

bot = commands.Bot(command_prefix='!', description='Economy Bot', intents=intents)
logging.basicConfig(level=logging.INFO)

# slashcom = discord.slash_command()
cluster = MongoClient(
    config.database)
db = cluster["DiscordEconomy"]

econposts = db.economy  # collection for Updating Economy Posts
crimeprompt = db.crimeprompts  # collection for Crime Prompts#
crimefail = db.crimefail  # collection for Crime Failures
workprompt = db.workprompts  # collection for Work Prompts
slutprompt = db.slutprompts  # collection for Slut Prompts
slutfail = db.slutfail  # collection for Slut Failures

crimemax = crimeprompt.count_documents({})
crimemaxfail = crimefail.count_documents({})
workmax = workprompt.count_documents({})
slutmax = slutprompt.count_documents({})
slutmaxfail = slutfail.count_documents({})


# ------------------------------------


@bot.event
async def on_ready():  # When the bot is ready will post these things
    print('Logged in as')
    print(bot.user.name)
    # print(client.user.id)
    print('Economy Online')
    print('------')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        seconds = round(error.retry_after) % (24 * 3600)
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        if minutes == 0:
            await ctx.send(f'You are on cooldown for {seconds} seconds')
        else:
            await ctx.send(f'You are on cooldown for {minutes} minutes and {seconds} seconds')


class Economy(commands.Cog):
    """All Economy Commands"""

    @commands.command(
        name="work",
        aliases=["Work"],
        brief="Work and Gain Money",
        help="Use this command to earn money legally",
    )
    @commands.cooldown(1, 300, commands.BucketType.user)
    async def _work(self, ctx):
        money = random.randint(1, 10)  # Randomly generate an amount of money
        promptnum = random.randint(1, workmax)  # Generate a random number for the prompt id
        findprompt = workprompt.find_one({"_id": str(promptnum)})
        await ctx.send(str(findprompt["Prompt"]) + "{}".format(money))
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
    @commands.cooldown(1, 120, commands.BucketType.user)
    async def _crime(self, ctx):
        money = random.randint(20, 50)  # Generate a random amount of money
        chance = random.randint(1, 2)  # Determines if the user will be caught (success) or not (fail)
        if chance == 1:  # If the user is caught
            try:  # If the user has never had an entry in the database
                balance = {"_id": str(ctx.message.author.id),
                           "Name": str(ctx.message.author.name),
                           "Balance": int(-money),
                           "CreatedDate": datetime.datetime.utcnow(),
                           "UpdatedDate": datetime.datetime.utcnow()}
                econposts.insert_one(balance)
                await ctx.send("Your Balance is now $" + str(balance["Balance"]))
            except:  # If the user has an entry in the database
                failnum = random.randint(1, crimemaxfail)  # Generate a random number for the fail prompt id
                findprompt = crimefail.find_one({"_id": str(failnum)})
                searchbyId = econposts.find_one({"_id": str(ctx.message.author.id)})
                idBalance = searchbyId["Balance"]
                filter = {"_id": str(ctx.message.author.id)}
                newbalance = {"$set": {"Balance": idBalance - money}}
                econposts.update_one(filter, newbalance)
                econposts.update_one(filter, {"$set": {"UpdatedDate": datetime.datetime.utcnow()}})
                NewSearchofID = econposts.find_one({"_id": str(ctx.message.author.id)})
            await ctx.send(str(findprompt["Prompt"]) + "{}".format(money))  # Send the user the amount of money lost
            await ctx.send("You now have $" + str(NewSearchofID["Balance"]))  # Send the user their new balance
        else:  # If the user is not caught
            promptnum = random.randint(1, crimemax)  # Generate a random number for the prompt id
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

    @commands.command(
        name="slut",
        aliases=["Slut"],
        brief="Do a sexual act to Gain Money",
        help="Use this command to earn money illegally and sexually"
    )
    @commands.cooldown(1, 120, commands.BucketType.user)
    async def _slut(self, ctx):
        money = random.randint(10, 40)  # Generate a random amount of money
        chance = random.randint(1, 2)  # Determines if the user will be caught (success) or not (fail)
        if chance == 1:  # If the user is caught
            try:  # If the user has never had an entry in the database
                balance = {"_id": str(ctx.message.author.id),
                           "Name": str(ctx.message.author.name),
                           "Balance": int(-money),
                           "CreatedDate": datetime.datetime.utcnow(),
                           "UpdatedDate": datetime.datetime.utcnow()}
                econposts.insert_one(balance)
                await ctx.send("Your Balance is now $" + str(balance["Balance"]))
            except:  # If the user has an entry in the database
                failnum = random.randint(1, slutfail)  # Generate a random number for the fail prompt id
                findprompt = slutfail.find_one({"_id": str(failnum)})
                searchbyId = econposts.find_one({"_id": str(ctx.message.author.id)})
                idBalance = searchbyId["Balance"]
                filter = {"_id": str(ctx.message.author.id)}
                newbalance = {"$set": {"Balance": idBalance - money}}
                econposts.update_one(filter, newbalance)
                econposts.update_one(filter, {"$set": {"UpdatedDate": datetime.datetime.utcnow()}})
                NewSearchofID = econposts.find_one({"_id": str(ctx.message.author.id)})
            await ctx.send(str(findprompt["Prompt"]) + "{}".format(money))  # Send the user the amount of money lost
            await ctx.send("You now have $" + str(NewSearchofID["Balance"]))  # Send the user their new balance
        else:  # If the user is not caught
            promptnum = random.randint(1, slutmax)  # Generate a random number for the prompt id
            findprompt = slutprompt.find_one({"_id": str(promptnum)})  # Find the prompt
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

    @commands.command(
        name="gamble",
        aliases=["Gamble"],
        brief="Gamble set amount of money",
        description="Gamble set amount of money",
        usage="gamble <amount>",
        help="Gamble set amount of money",
        guild_only=True
    )
    @commands.cooldown(rate=3, per=120, type=commands.BucketType.user)
    async def _gamble(self, ctx, money: int):
        try:  # If the user has never had an entry in the database
            balance = {"_id": str(ctx.message.author.id),
                       "Name": str(ctx.message.author.name),
                       "Balance": int(0),
                       "CreatedDate": datetime.datetime.utcnow(),
                       "UpdatedDate": datetime.datetime.utcnow()}
            econposts.insert_one(balance)
            await ctx.send("Your Balance is now $" + str(balance["Balance"]))
            print("Error")
        except:  # If the user has an entry in the database
            chance = random.randint(1, 2)
            searchbyId = econposts.find_one({"_id": str(ctx.message.author.id)})
            idBalance = searchbyId["Balance"]
            filter = {"_id": str(ctx.message.author.id)}
            if money > idBalance:  # If the user tries to gamble more than they have
                await ctx.send("You do not have enough money to gamble that much")
            else:  # If the user has enough money to gamble
                if money < 0:  # Trying gamble negative money
                    await ctx.send("You cant gamble negative money")
                elif money == 0:  # trying to gamble 0 money
                    await ctx.send("You cant gamble 0 money")
                elif money > 0:  # trying to gamble normal money
                    if chance == 1:  # If the user wins
                        await ctx.send("You won!")
                        newbalance = {"$set": {"Balance": idBalance + money}}
                        econposts.update_one(filter, newbalance)
                        econposts.update_one(filter, {"$set": {"UpdatedDate": datetime.datetime.utcnow()}})
                        NewSearchofID = econposts.find_one({"_id": str(ctx.message.author.id)})
                        await ctx.send("You now have $" + str(NewSearchofID["Balance"]))
                    if chance == 2:
                        await ctx.send("You lost!")
                        newbalance = {"$set": {"Balance": idBalance - money}}
                        econposts.update_one(filter, newbalance)
                        econposts.update_one(filter, {"$set": {"UpdatedDate": datetime.datetime.utcnow()}})
                        NewSearchofID = econposts.find_one({"_id": str(ctx.message.author.id)})
                        await ctx.send("You now have $" + str(NewSearchofID["Balance"]))
                else:
                    print("error")

    @commands.command(
        name="rob",
        aliases=["Rob"],
        brief="rob another user",
        help="Allows you to rob another user",
    )
    @commands.cooldown(rate=1, per=600, type=commands.BucketType.user)
    async def _rob(self, ctx, member: discord.Member):
        try:  # If the user has never had an entry in the database
            firstuserbalance = {"_id": str(ctx.message.author.id),
                                "Name": str(ctx.message.author.name),
                                "Balance": int(0),
                                "CreatedDate": datetime.datetime.utcnow(),
                                "UpdatedDate": datetime.datetime.utcnow()}
            econposts.insert_one(firstuserbalance)
            seconduserbalance = {"_id": str(ctx.message.member.id),
                                 "Name": str(ctx.message.member.name),
                                 "Balance": int(0),
                                 "CreatedDate": datetime.datetime.utcnow(),
                                 "UpdatedDate": datetime.datetime.utcnow()}
            econposts.insert_one(seconduserbalance)
            print("Error")
        except:  # If the user has an entry in the database
            chance = random.randint(1, 2)  # Decides if the user wins or loses
            searchbyId = econposts.find_one({"_id": str(ctx.message.author.id)})
            secondsearchbyId = econposts.find_one({"_id": str(member.id)})
            firstuseridBalance = searchbyId["Balance"]
            seconduseridBalance = secondsearchbyId["Balance"]
            filter = {"_id": str(ctx.message.author.id)}
            seconduserfilter = {"_id": str(member.id)}
            stolenamount = random.randint(1, seconduseridBalance/2)
            if member == ctx.message.author:  # Trying to rob yourself
                await ctx.send("You cant rob yourself")
            elif member != ctx.message.author:  # Trying to rob another user
                if seconduseridBalance < 50:  # If the user doesnt have enough money to rob
                    await ctx.send("You do not have enough money to rob that much")
                elif seconduseridBalance >= 50:  # If the user has enough money to rob
                    if chance == 1:  # If the user wins
                        await ctx.send("You robbed " + member.mention + " and stole $" + str(stolenamount))
                        newbalance = {"$set": {"Balance": firstuseridBalance + stolenamount}}
                        econposts.update_one(filter, newbalance)
                        econposts.update_one(filter, {"$set": {"UpdatedDate": datetime.datetime.utcnow()}})
                        NewSearchofID = econposts.find_one({"_id": str(ctx.message.author.id)})
                        await ctx.send("You now have $" + str(NewSearchofID["Balance"]))
                        secondusernewbalance = {"$set": {"Balance": seconduseridBalance - stolenamount}}
                        econposts.update_one(seconduserfilter, secondusernewbalance)
                        econposts.update_one(seconduserfilter, {"$set": {"UpdatedDate": datetime.datetime.utcnow()}})

                    if chance == 2:  # If the user loses
                        await ctx.send(
                            "You failed to rob " + member.mention + " and instead you lost $" + str(stolenamount))
                        newbalance = {"$set": {"Balance": firstuseridBalance - stolenamount}}
                        econposts.update_one(filter, newbalance)
                        econposts.update_one(filter, {"$set": {"UpdatedDate": datetime.datetime.utcnow()}})
                        NewSearchofID = econposts.find_one({"_id": str(ctx.message.author.id)})
                        await ctx.send("You now have $" + str(NewSearchofID["Balance"]))
                else:
                    print("error")
            else:
                print("error")



@bot.slash_command(guild_ids=[917236140422070283], name="ping", description="Get bot ping")
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')
    print("Ping Command Was Run")


bot.add_cog(Economy(bot))
bot.run(config.token)
