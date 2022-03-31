from quart import Quart, render_template, request, jsonify, redirect, url_for, session, g, send_from_directory
from quart_discord import DiscordOAuth2Session, requires_authorization, Unauthorized
import os
import config
from pymongo import MongoClient
import discord
intents = discord.Intents.all()
intents.members = True

# -----------------------------------------------------------------------------------------------------------------------
# from economy import econposts

app = Quart(__name__)
app.secret_key = config.session
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"
app.config["DISCORD_CLIENT_ID"] = config.CLIENT_ID
app.config["DISCORD_CLIENT_SECRET"] = config.CLIENT_SECRET
app.config["DISCORD_REDIRECT_URI"] = config.RI
app.config["DISCORD_BOT_TOKEN"] = config.token

discordd = DiscordOAuth2Session(app)


# -----------------------------------------------------------------------------------------------------------------------

cluster = MongoClient(
    config.database)
db = cluster["DiscordEconomy"]

econposts = db.economy  # collection for Updating Economy Posts
crimeprompt = db.crimeprompts  # collection for Crime Prompts#
workprompt = db.workprompts  # collection for Work Prompts

# -----------------------------------------------------------------------------------------------------------------------

@app.route("/")
async def home():
    logged = ""
    lst = []
    data = {}
    balance = 0
    if await discordd.authorized:
        logged = True
        user = await discordd.fetch_user()
        try:
            searchbyId = econposts.find_one({"_id": str(user.id)})
            idBalance = searchbyId["Balance"]
            balance = idBalance
            print(idBalance)
            print("User is logged in")
        except:
            balance = 0
            print(user.id)
            print(searchbyId)
            print(idBalance)
    return await render_template("index.html", logged=logged, balance=balance)


@app.route("/login/")
async def login():
    return await discordd.create_session()


@app.route("/logout/")
async def logout():
    discordd.revoke()
    return redirect(url_for(".home"))


@app.route("/me/")
@requires_authorization
async def me():
    user = await discordd.fetch_user()
    return redirect(url_for(".home"))


@app.route("/callback/")
async def callback():
    await discordd.callback()
    try:
        return redirect(url_for(".me"))
    except:
        return redirect(url_for(".home"))


@app.errorhandler(Unauthorized)
async def redirect_unauthorized(e):
    # bot.url = request.url
    return redirect(url_for(".login"))


app.run()
