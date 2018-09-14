import re
import codecs
import time
import random
import discord
import shutil
import subprocess
import os
from datetime import datetime
from discord.ext import commands
from random import randint


class General:
    """
    General Chat Commands
    """

    # Construct
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    # Send message
    async def send(self, msg):
        await self.bot.say(msg)

    # Commands
    @commands.command()
    async def uptime(self):
        """Shows bot uptime"""

        uptime = datetime.today() - self.bot.start_time
        msg = "My uptime is {}".format(uptime)
        await self.send(msg)

    @commands.group(pass_context=True)
    async def div(self, ctx):
        """Shows current wordline divergence"""

        if ctx.invoked_subcommand is None:
            date = datetime.today()
            calc = (date.day + date.month + date.year) / 13.35
            div = "{}.{}".format(date.month % 4, str(calc)[6:12])

            msg = "Current divergence is: {}".format(div)
            await self.send(msg)

    @div.command(pass_context=True, name="meter")
    async def div_meter(self, ctx):
        """Graphical divergence meter"""

        date = datetime.today()
        calc = (date.day + date.month + date.year) / 13.35
        div = "{}.{}".format(date.month % 4, str(calc)[6:12])

        storage = []

        if not os.path.isfile("divs/{}.png".format(div)):
            for number in div:
                if number == ".":
                    storage.append("nums/point.png")
                else:
                    storage.append("nums/{}.png".format(number))

            result = shutil.which('convert')

            if result:
                command = "convert {} +append divs/{}.png".format(" ".join(storage), div).split()
                try:
                    subprocess.check_call(command)
                except subprocess.CalledProcessError:
                    print('Error')

        file = open('divs/{}.png'.format(div), 'rb')
        await self.bot.send_file(ctx.message.channel, file)
        file.close()

    @commands.command()
    async def stickers(self):
        """Shows available stickers"""

        embeded = discord.Embed(title="List of available stickers", color=0xEE8700)

        for sticker in self.bot.stickers:
            embeded.add_field(name=sticker, value=self.bot.stickers[sticker], inline=True)

        await self.bot.say(embed=embeded)

    @commands.command(pass_context=True, name="chart-h")
    async def chart_h(self, ctx):
        """Shows activity chart using last 100 msgs"""

        storage = {}


        async for message in self.bot.logs_from(ctx.message.channel, limit=100):
            if message.author.name not in storage:
                r = lambda: random.randint(0, 255)
                storage.update({message.author.name: {"color": '%02X%02X%02X' % (r(), r(), r()), "messages_count": 0}})
            storage[message.author.name]["messages_count"] += 1

        users = []
        colors = []
        counts = []

        for key, value in storage.items():
            u = re.sub('\s+', '+', key)

            users.append(u)
            colors.append(value['color'])
            counts.append(value['messages_count'])

        link = "https://chart.apis.google.com/chart?cht=p&chs=740x405&chdl={}&chl={}&chco={}&chd=t:{}&chtt=Who's+talking".format(
            "|".join(users), "|".join(users), "|".join(colors), ",".join(map(str, counts))
        )

        await self.send(link)

    @commands.command()
    async def waifu(self, content: str):
        """Shows waifu's (and not only) rating"""

        await self.send("I'm of the opinion {} deserves **{}%** on the Faris meter".format(content, str(randint(0, 100))))

    @commands.command(pass_context=True)
    async def rot13(self, ctx, *, content: str):
        """Spoiler protection system 1.41"""

        bot = ctx.message.server.get_member(self.bot.user.id)
        permissions = ctx.message.channel.permissions_for(bot)

        if not permissions.manage_messages:
            await self.bot.send_message(ctx.message.channel, "I can't delete messages without `Manage messages` permission!")
            return

        await self.bot.delete_message(ctx.message)

        encoded = codecs.encode(content, 'rot_13')

        await self.bot.send_message(ctx.message.channel, "{} > {}".format(ctx.message.author.name, encoded))

    @commands.command(pass_context=True)
    async def dice(self, ctx):
        """Rolls dice"""

        await self.bot.send_message(ctx.message.channel, "{} rolled **{}**".format(ctx.message.author.name, str(randint(1, 6))))

    @commands.command()
    async def future(self, *, content: str):
        """Ever wanted to use the time machine?"""

        def get_prediction(num):
            return {
                6 <= num <= 10: "You're going full delusional",
                4 <= num < 6: "It looks like @channel has no resources about this",
                num < 4: "Faris says it looks good, believe the waifu"
            }[True]

        date = datetime.today()

        number = (date.day + date.year + date.month) / 14
        number = len(content) / number
        number = str(number)[4:5]
        msg = get_prediction(int(number))

        await self.bot.say(msg)

    @commands.command()
    async def nsfw(self, *, tags: str):
        """Shows NSFW stuff"""

        # Need to figure out how to work with HTTP in python ¯\_(ツ)_/¯
        pass

    @commands.command(pass_context=True)
    async def sonome(self, ctx):
        """Dare no me?"""

        bot = ctx.message.server.get_member(self.bot.user.id)
        permissions = ctx.message.channel.permissions_for(bot)

        if not permissions.manage_messages:
            await self.bot.send_message(ctx.message.channel, "I can't delete messages without `Manage messages` permission!")
            return

        await self.bot.delete_message(ctx.message)

        msg = "fun^10 X int^40 = ir2" if randint(0, 10) == 0 else "その目だれの目？"

        await self.send(msg)
    
    @commands.group(pass_context=True, name="run")
    async def run(self, ctx, *, word : str):
        """Running word"""

        if len(word) > 10:
            await self.send("Word may not be longer than 10 letters.")
            return

        display = "####"
        oword = ctx.message.clean_content[5:] + "####"
        nword = ctx.message.clean_content[5:] + "####"
        olist = []
        nlist = []

        for c in oword:
            olist.append(c)

        for c in nword:
            nlist.append(c)

        await self.send(display)
        msg = ""

        async for cmsg in self.bot.logs_from(ctx.message.channel, limit = 1):
            msg = cmsg

        self.bot.delete_message(ctx.message)

        i = 0
        n = 0
        while n < 14:
            if i==0:
                await self.bot.edit_message(msg, ''.join(nlist))
                n+=1
                olist = nlist[:]
                time.sleep(1)
            nlist[i-1] = olist[i]
            i = (i + 1) % len(nlist)

def setup(bot):
    bot.add_cog(General(bot))

