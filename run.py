#!/usr/bin/env python3

# Codebase: https://github.com/RIP95/kurisu-bot

# Import dependencies
import os, sys
import json
import random
import sqlite3
from discord.ext import commands
from datetime import datetime

description = """
I am Daru, The Supah Hackah!
Project source code: To Be Written

Here is the list of available commands:
"""

# Set working directory to bot's folder
dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)

prefixes = ['/']
bot = commands.Bot(command_prefix=prefixes, description=description, pm_help=None)

bot.pruning = False  # used to disable leave logs if pruning, maybe.

# Read config
if not os.path.isfile("config.json"):
    sys.exit("Set up your config.json file first!")

with open('config.json') as data:
    bot.config = json.load(data)

# Initialize db connection
bot.db = sqlite3.connect('chat.db')
bot.cursor = bot.db.cursor()

bot.stickers = {
    "/nice":     "https://i.imgur.com/7zthtFQ.jpg",
    "/counting": "https://i.imgur.com/OckHKoS.png",
    "/okay":     "https://i.imgur.com/FcrUVuB.png",
    "/srsly":    "https://i.imgur.com/jyZPMec.png",
    "/sorry":    "https://i.imgur.com/ZvBm2GL.png",
    "/refuse":   "https://i.imgur.com/vevF4bt.png",
    "/orz":      "https://i.imgur.com/52JTsQX.png",
    "/ntmy":     "https://i.imgur.com/LZbXegV.png",
    "/huh":      "https://i.imgur.com/bE8s2Yg.png",
    "/hmpf":     "https://i.imgur.com/uvbhPnV.png",
    "/blush":    "https://i.imgur.com/yxDNKXX.png",
    "/wap":      "https://i.imgur.com/G7yEeTU.png",
    "/wut":      "https://i.imgur.com/MHpKssf.png",
    "/del":      "https://i.imgur.com/UkGV1ss.png",
    "/wat":      "https://i.imgur.com/UiWL1ib.png",
    "/amds":     "https://i.imgur.com/P6N2wBA.png",
    "/ruok":     "https://i.imgur.com/yD0I0KB.png",
    "/shock":    "https://i.imgur.com/5sDp6KU.png",
    "/omw":      "https://i.imgur.com/HJBHst5.png",
    "/exorcism": "https://i.imgur.com/vgWXAjC.png",
    "/perfect":  "https://i.imgur.com/Nd5KT0G.png",
    "/alpacaman":"https://i.imgur.com/RoyPPRx.png",
    "/gnight":   "https://i.imgur.com/CJZcQwD.png",
    "/gratz":	 "https://i.imgur.com/uct0wtH.png",
    "/same":	 "https://i.imgur.com/UKSWRYJ.jpg"
}


@bot.event
async def on_command_error(ecx, ctx):
    if isinstance(ecx, commands.errors.MissingRequiredArgument):
        formatter = commands.formatter.HelpFormatter()
        await bot.send_message(ctx.message.channel, "You are missing required arguments. See the usage:\n{}".format(formatter.format_help_for(ctx, ctx.command)[0]))


@bot.event
async def on_message(msg):

    if msg.author.bot:
        return

    # DB log section
    date = msg.timestamp.isoformat()
    name = msg.author.name
    content = msg.clean_content
    if msg.attachments:
        content = "{} {}".format(content, msg.attachments[0]['url'])
    nick = "bot"

    try:
        server = msg.server.name
        server_ID = msg.server.id
    except AttributeError:
        server = "Private messages"
        server_ID = 0

    if not msg.channel.is_private:
        channel = msg.channel.name
    else:
        channel = "dmc"

    if hasattr(msg.author, 'nick'):
        nick = msg.author.nick

    data = (server, name, nick, content, date, channel, server_ID)

    bot.db.execute("INSERT INTO dis VALUES (?,?,?,?,?,?,?)", data)
    bot.db.commit()

    print("Message has been written to DB")

    # Process stickers
    for key, value in bot.stickers.items():
        if content.lower().startswith(key):
            await bot.send_message(msg.channel, value)
            return

    exceptions = ['/sql', '/hist', '/ran', '/exec']

    for exception in exceptions:
        if content.lower().startswith(exception):
            return

    await bot.process_commands(msg)

    #Dsmn
    if msg.channel.is_private: return

    mbrs = msg.server.members
    r = random.randint(0, 180)
    if r != 10: return

    addon = bot.cogs['Dsmn']

    addon.dsmn = random.sample(list(mbrs), 1)[0]
    name = addon.dsmn.name
    
    if msg.server.id != 340928102509182989:
        await bot.send_message(msg.channel, name + " is sensing a gaze'... \n\n*Use /boot to realboot the delusion.*")

@bot.event
async def on_ready():

    bot.start_time = datetime.today()
    print("{} has started!".format(bot.user.name))
    print("Current time is {}".format(bot.start_time))
    for server in bot.servers:
        print("Connected to {} with {:,} members!".format(server.name, server.member_count))
    #await bot.change_presence(game=discord.Game(name='Kurisu, help | El.Psy.Kongroo'))

# Load extensions
print("Loading addons:")
for extension in bot.config['extensions']:
    try:
        bot.load_extension(extension['name'])
    except Exception as e:
        print('{} failed to load.\n{}: {}'.format(extension['name'], type(e).__name__, e))

# Use token for bot or email/password for user account
# bot.run(bot.config['token'])
bot.run(bot.config['email'], bot.config['password'])
