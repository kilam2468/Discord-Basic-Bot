import discord
import os
from discord.ext import commands
import config
from discord import ClientException
from discord.ext import commands
from pretty_help import DefaultMenu, PrettyHelp
from asyncio import sleep
import random

bot = commands.Bot(command_prefix='!', description='Economy Bot')


@bot.event
async def on_ready():  # When the bot is ready will post these things
    print('Logged in as')
    print(bot.user.name)
    # print(client.user.id)
    print('Voice Online')
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
        brief="Work and Gain Money",
        help="Use this command to earn money legally",
        usage=""

    )
    async def _work(self, ctx):
        money = random.randint(1, 10)
        await ctx.send("You worked and earned {}".format(money))
        await ctx.send("You now have $" + str(HOLDER))


bot.add_cog(Economy(bot))
bot.run(config.token)
