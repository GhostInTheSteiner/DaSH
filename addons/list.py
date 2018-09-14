import re
import discord
import random
import codecs
import sqlite3
from datetime import datetime
from discord.ext import commands
from random import randint

class List:
    """
    List
    """

    # Construct
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    # Send message
    async def send(self, msg):
        await self.bot.say(msg)

    # Commands
    @commands.command(pass_context=True, name="list-a")
    async def alist(self, ctx, trigger : str, *, text : str):
        """Adds items to a list"""
        
        if "```" in trigger: return

        entry = text.replace("@everyone", "everyone").replace("@here", "here")
        data = (entry, trigger)

        try:
            self.bot.cursor.execute("INSERT INTO list VALUES(?, ?)", data)
            self.bot.db.commit()
            await self.send("Entry added to list.")
        except:
            await self.send("Don't even try overwriting.")

    @commands.command(pass_context=True, name="list-g")
    async def glist(self, ctx, trigger : str):
        """Gets items from list"""

        self.bot.cursor.execute("SELECT entry FROM list WHERE trigger = ?", (trigger,))
        rows = self.bot.cursor.fetchall()

        if len(rows) > 0:
            await self.send(rows[0][0])
        else:
            await self.send("You know, I even went as far as looking through my yuri collection, but I wasn't able to find anything ( ͠° ͟ʖ ͡°)")            
    
        # Commands
    @commands.command(pass_context=True, name="list-d")
    async def dlist(self, ctx, trigger : str):
        """Delete items from list"""
        
        if ctx.message.author.id != "127658424082104320":
            await self.send("I'll only ever allow you to do this if you start using ('_v')")
            return

        if self.bot.cursor.execute("DELETE FROM list WHERE trigger = ?", (trigger,)).rowcount > 0:
            self.bot.db.commit()
            await self.send("Deleted.")
        else:
            await self.send("Row not found.")
        
    @commands.command(pass_context=True, name="list-s")
    async def slist(self, ctx):
        """Shows the list"""

        self.bot.cursor.execute("SELECT trigger FROM list")
        rows = self.bot.cursor.fetchall()

        list = "```\n"

        for row in rows:
            list += row[0] + "\n"

        list += "```"
        
        await self.send(list)

def setup(bot):
    bot.add_cog(List(bot))
