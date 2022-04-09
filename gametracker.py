import config as config
import discord
from discord import Embed
import os
from discord.ext import commands
import config
import logging
import requests
from discord.ui import Button, View
import fortnite_api
from fortnite_api import StatsImageType
import shutil
import time

intents = discord.Intents.all()
intents.members = True

client = commands.Bot(command_prefix='!', intents=intents)
logging.basicConfig(level=logging.INFO)

fortapi = fortnite_api.FortniteAPI(api_key=config.FORTAPIKEY, run_async=False)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    # print(client.user.id)
    print('Game Tracker Online')
    print('------')


@client.command()
async def profile(ctx):
    button1 = Button(label='Apex Legends', style=discord.ButtonStyle.red, custom_id='Apex')
    button2 = Button(label='Fortnite', style=discord.ButtonStyle.blurple, custom_id='Fortnite')

    async def button_callback(interaction):
        time.sleep(1)
        await interaction.response.edit_message(content="You pressed: " + interaction.custom_id, view=None)
        pressed = interaction.custom_id
        if pressed == 'Apex':
            await ctx.send("What Platform are you on?")
            platform = await client.wait_for('message', timeout=60.0)
            if platform.content == 'pc':
                platform = 'origin'  # PC is the same as Origin
            elif platform.content == 'xbox':
                platform = 'xbl'
            elif platform.content == 'psn':
                platform = 'psn'
            elif platform.content == 'steam':
                platform = 'origin'
            elif platform.content == 'origin':
                platform = 'origin'
            else:
                await ctx.send('Please enter a valid platform')
                return
            await ctx.send("What is your username?")
            username = await client.wait_for('message', timeout=60.0)
            await ctx.send('Please wait...')
            url = 'https://public-api.tracker.gg/v2/apex/standard/profile/{}/{}'.format(platform, username.content)
            headers = {'TRN-Api-Key': config.APEXAPIKEY, 'Accept': 'application/json'}
            r = requests.get(url, headers=headers)
            if r.status_code == 200:
                data = r.json()
                userid = data['data']['platformInfo']['platformUserId']
                avatarurl = data['data']['platformInfo']['avatarUrl']
                lifetime = data['data']['segments'][0]['stats']
                apexlevel = lifetime['level']['displayValue']
                apexkills = lifetime['kills']['displayValue']
                try:
                    apexdamage = lifetime['damage']['displayValue']
                    apexheadshots = lifetime['headshots']['displayValue']
                except:
                    apexdamage = 'N/A'
                    apexheadshots = 'N/A'
                apexrankscore = lifetime['rankScore']['metadata']['rankName']
                apexrankpic = lifetime['rankScore']['metadata']['iconUrl']
                apexembed = Embed(type='rich',
                                  title='Apex Stats for ' + userid,
                                  description='',
                                  color=discord.Color.brand_red(),
                                  )
                apexembed.add_field(name='Level', value=apexlevel, inline=True)
                apexembed.add_field(name='Kills', value=apexkills, inline=True)
                apexembed.add_field(name='Damage', value=apexdamage, inline=True)
                apexembed.add_field(name='Headshots', value=apexheadshots, inline=True)
                apexembed.add_field(name='Rank', value=apexrankscore, inline=True)
                apexembed.set_thumbnail(url=avatarurl)
                apexembed.set_image(url=apexrankpic)
                await ctx.send(embed=apexembed)
            else:
                print(url)
                print(r.status_code)
                print("PROBLEM")
                await ctx.send("There was a problem with your request. Please recheck and try again.")
                return None

        elif pressed == 'Fortnite':
            await ctx.send("What Platform are you on?")
            platform = await client.wait_for('message', timeout=60.0)
            if platform.content == 'pc':
                platform = 'pc'
            elif platform.content == 'xbox':
                platform = 'xbl'
            elif platform.content == 'psn':
                platform = 'psn'
            elif platform.content == 'steam':
                platform = 'steam'
            elif platform.content == 'origin':
                platform = 'origin'
            else:
                await ctx.send('Please enter a valid platform')
                return
            await ctx.send("What is your username?")
            username = await client.wait_for('message', timeout=60.0)
            try:
                fortdata = fortapi.stats.fetch_by_name(name=username.content, image=StatsImageType('all')).raw_data
            except fortnite_api.errors.NotFound:
                await ctx.send("User not found")
                return
            imageurl = fortdata['image']
            file_name = 'fortnitestat.png'
            res = requests.get(imageurl, stream=True)
            if res.status_code == 200:
                with open(file_name, 'wb') as f:
                    shutil.copyfileobj(res.raw, f)
                print('Image successfully Downloaded: ', file_name)
                await ctx.send(content='Here is your Fortnite Stats:', file=discord.File(file_name))
                os.remove(file_name)
                print('Image removed: ', file_name)
            else:
                print('Image Couldn\'t be retrieved')
                return

    button1.callback = button_callback
    button2.callback = button_callback
    view = View()
    view.add_item(button1)
    view.add_item(button2)

    await ctx.send('What Game?', view=view)


client.run(config.token)
