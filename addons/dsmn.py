import traceback
import discord
import random
import sqlite3
import time
import asyncio
from .dbfun import DBFun
from datetime import datetime
from discord.ext import commands
from random import randint

class Dsmn:
    """
    Dsmn
    """

    # Construct
    def __init__(self, bot):
        self.game = {'state': 'nothing', 'aid1': '', 'aid0': '', 'anm1': '', 'anm0': '', 'atker': '', 'plr1': '', 'plr0': '', 'dsmn1': '', 'dsmn0': '', 'dst': '', 'mbrs': ''}
        self.trd = {'state': 'nothing', 'dsmn1': '', 'dsmn0': '', 'otr': ''}
        self.bot = bot
        self.amo = {}
        self.dbfun = DBFun(bot)
        self.dsmn = None
        self.amo_upd()
        self.attemptedCancel = False

        print('Addon "{}" loaded'.format(self.__class__.__name__))

    def arow_gnr(self):
        self.amo_upd()
        dsmnid = self.amo['dsmn']
        
        amount = self.amo['abt']
        abtids = random.sample(range(1, amount+1), 4)

        rows = []

        for abtid in abtids:
            rows.append((dsmnid, abtid))

        return rows

    def amo_upd(self):
        self.amo['type'] = self.dbfun.amo("type")
        self.amo['dsmn'] = self.dbfun.amo("dsmn")
        self.amo['abt'] = self.dbfun.amo("abt")
        self.amo['arow'] = self.dbfun.amo("arow")

    def exp_incr(self, dsmn, val):
        data = self.dbfun.expbase(dsmn)
        lvlupstp = data[0]
        olvl = data[1]
        nxp = data[2]+val
        nck = data[3]
        if lvlupstp <= nxp: nlvl = nxp//lvlupstp
        else: nlvl = 1
        
        info = ""

        if olvl < nlvl:
            info = " ***" + nck + "*** increased its level to ***" + str(nlvl) + "***\n"
            nxp += random.randint(lvlupstp, lvlupstp+40)
        
        info += "***" + nck + "*** increased its exp to ***" + str(nxp) + "***"

        self.dbfun.updsts(dsmn, nlvl, nxp)
        
        return info

    async def fight(self, d1, d0, a1, a0):
        for row in self.dbfun.fgtbase(d1, d0, a1, a0):
            print(row)
            if str(row[1]) == d1:
                print("d1")
                d1 = {'nick': row[3], 'info': row[5], 'lvl': row[2], 'exp': row[0], 'id': d1}
            if str(row[1]) == d0:
                print("d0")                
                d0 = {'nick': row[3], 'info': row[5], 'lvl': row[2], 'exp': row[0], 'id': d0}

        d1lvl = self.clvl(str(d1['lvl']), str(d0['lvl']))
        d0lvl = self.clvl(str(d0['lvl']), str(d1['lvl']))
        dst = self.game['dst']
        r1 = random.randint(10, 14)
        r0 = random.randint(1, 6)
        d1nck = d1['nick']
        d0nck = d0['nick']        
        info1 = d1['info']
        info0 = d0['info']        
        d1exp = d1['exp']
        d0exp = d0['exp']
        d1id = d1['id']
        d0id = d0['id']
        if d1exp*d1lvl > d0exp*d0lvl:
            await self.send(info1, dst=dst)
            time.sleep(0.5)
            info = self.exp_incr(d1id, r1)
            await self.send(info, dst=dst)
            info = self.exp_incr(d0id, r0)
            await self.send(info, dst=dst)
            winner = d1nck

        if d1exp*d1lvl < d0exp*d0lvl:
            await self.send(info0, dst=dst)
            time.sleep(0.5)
            info = self.exp_incr(d0id, r1)
            await self.send(info, dst=dst)
            info = self.exp_incr(d1id, r0)
            await self.send(info, dst=dst)
            winner = d0nck        

        if d1exp*d1lvl == d0exp*d0lvl:
            info = self.exp_incr(d0id, r1)
            await self.send(info, dst=dst)
            info = self.exp_incr(d1id, r0)
            await self.send(info, dst=dst)
            winner = 'noone'
        return winner

    def embfact(self, description, usrimg, title, fields=None, image=None):
        em = discord.Embed(title=title, description=description, colour=0x9C8914)

        if image != None: em.set_image(url=image)

        if type(fields) is dict:    
            em.set_author(name=fields['name'], icon_url=usrimg)
            for f in fields:
                em.add_field(value=fields[f], name=f, inline=False)
        else:
            em.set_author(name="Info", icon_url=usrimg)
        return em

    def userbyid(self, mbrs, id):
        for member in mbrs:
            if member.id == id:
                return member

    async def slist(self, name, id, tab, dst=None):
        level = "Lvl "
        br1 = "*["
        br0 = "]*"
        if tab == "abt":
            info = "'s delusions' Di-Sword allows the following attacks:"
            level = ""
        if tab == "dsmn":
            info = " has realbooted the following delusions:"

        rows = self.dbfun.listbase(id, tab)
        list = ""

        for row in rows:
            list += "***" + str(row[0]) + "***    " + row[2] + "    " + br1 + level + str(row[1]) + br0 +"\n"

        list += ""
        title = name + info
        avt = self.bot.connection.user.avatar_url

        em = self.embfact(list, avt, title)
        await self.send('', em=em, dst=dst)

    def info(self, id, tab):
        fields = {}

        if tab == "dsmn":
            vals = list(self.dbfun.infobase(id, "dsmn"))
            dsr = self.bot.cursor.description
            names = list(map(lambda x: x[0], dsr))
            avatar = vals[2]
            del(names[2])
            del(vals[2])
            image = avatar

        if tab == "type":
            vals = list(self.dbfun.infobase(id, "type"))
            dsr = self.bot.cursor.description
            names = list(map(lambda x: x[0], dsr))
            avatar = self.bot.user.avatar_url
            image = None

        for i in range(0, len(vals)):
            fields[names[i]] = vals[i]
        return self.embfact('', avatar, '', fields, image)

        
    def clvl(self, l1, l0):
        rst = {'StrategyDefense':1.0,'StrategyOffense':0.5,'DefenseStrategy':0.5,'DefenseOffense':1.0,'OffenseStrategy':1.0,'OffenseDefense':0.5}
        data1 = l1+l0
        data0 = l0+l1
        if data1 in rst: rst = [rst[data1], rst[data0]]
        else: rst = [1.0, 1.0]
        return rst[0]

    # Send message
    async def send(self, msg, em=None, dst=None):
        if dst != None:
            await self.bot.send_message(dst, msg, embed=em)
        else:            
            await self.bot.say(msg, embed=em)

    @commands.command(pass_context=True, name="init")
    async def init(self, ctx):
        info = "Spyro"

    @commands.command(pass_context=True, name="boot")
    async def catch(self, ctx):
        """Realboot a delusionary existence"""

        if self.dsmn == None:
            await self.send("No delusion spawned, you'll have to wait until the next one does.")        
            return

        roles = []

        for r in self.dsmn.roles:
            roles.append(r.name)

        roles = ','.join(roles)

        game = None

        master = ctx.message.author.id
        if hasattr(game, 'name'): game = self.dsmn.game.name
        born = str(self.dsmn.created_at)
        avatar = self.dsmn.avatar_url
        name = self.dsmn.name
        uid = self.dsmn.id
        nick = self.dsmn.display_name
        colour = self.dsmn.colour.value

        exp = 1
        level = 1

        type = random.sample(range(1, self.amo['type']+1), 1)[0]

        await self.send(ctx.message.author.name + " successfully realbooted a delusionary existence. \n\n*Use /try @<name> **within the <#215875343335030785> channel** to start a match with another gigalomaniac.*")

        data = (name, game, nick, roles, exp, uid, level, avatar, colour, master, born, type)
        self.dbfun.insert(data, "dsmn")
        ctx.bot.db.commit()
        
        for row in self.arow_gnr():
            self.dbfun.insert(row, "arow")

        self.dsmn = None

    @commands.command(pass_context=True, name="force-cnl")
    async def forcecnl(self, ctx):
        """Enforce a running game to end"""    

        if self.attemptedCancel:
            self.game = {'state': 'nothing', 'aid0': '', 'aid1': '', 'anm1': '', 'anm0': '', 'atker': '', 'plr0': '', 'plr1': '', 'dsmn0': '', 'dsmn1': ''}
            self.attemptedCancel = False
            await self.send("Game has been force-canceled due to user interaction.")

    @commands.command(pass_context=True, name="try")
    async def trya(self, ctx, name):
        """Try starting a match with another gigalomaniac"""

        if self.game['state'] != 'nothing':
            await self.send("It appears a game is currently running. If you believe someone left a game hanging you can force-cancel it by sending /force-cnl.")
            self.attemptedCancel = True
            return
        
        if ctx.message.channel.id != "215875343335030785":
            await self.send("Uuuuuhhhhhhhh...\n\nBro, I sure hope you didn't intend to do something bad. If you want to start a match then pleeeeeease **use <#215875343335030785> for that**, so you won't annoy others. \n\n'cause y'know, there will be a looooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooot of messages, and we both don't want to spam those into this channel, right?")
            return
        
        if ctx.message.author.id not in name and ctx.message.raw_mentions != [] and self.game['state'] == 'nothing': """"""
        else: return

        id = ctx.message.raw_mentions[0]

        if not self.dbfun.hasdsmns(id):
            await self.send("User didn't realboot any delusions.")
            return
            
        if not self.dbfun.hasdsmns(ctx.message.author.id):
            await self.send("You didn't realboot any delusions.")            
            return
        await self.send("Agree to the match with /acpt or decline with /cnl. **Please answer in any case!**")

        mbrs = ctx.message.server.members
        dst = ctx.message.channel
        
        mid = ctx.message.author.id
        self.game = {'state': 'waiting', 'aid0': '', 'aid1': '', 'anm1': '', 'anm0': '', 'atker': '', 'plr0': mid, 'plr1': id, 'dsmn0': '', 'dsmn1': '', 'dst': dst, 'mbrs': mbrs}

    @commands.command(pass_context=True, name="cnl")
    async def cnl(self, ctx):
        """Cancel the game"""
        
        if ctx.message.author.id in self.game.values(): """"""
        else:
            await self.send("Sorry. You're not taking part in this game, therefore you also are not allowed to cancel it.")  
            return

        self.game = {'state': 'nothing', 'aid0': '', 'aid1': '', 'anm1': '', 'anm0': '', 'atker': '', 'plr0': '', 'plr1': '', 'dsmn0': '', 'dsmn1': ''}
        await self.send("Game has been canceled due to user interaction.")

    @commands.command(pass_context=True, name="acpt")
    async def acpt(self, ctx):
        if ctx.message.author.id == self.game['plr1'] and self.game['state'] == 'waiting': """"""
        else: 
            await self.send("You're not the desired opponent.")  
            return

        r = random.randint(0, 10)
        if r > 5: self.game['atker'] = self.game['plr1']
        else: self.game['atker'] = self.game['plr0']

        members = ctx.message.author.server.members
        snd = self.game['plr1']
        fst = self.game['plr0']
        name1 = self.userbyid(members, snd).name
        name0 = self.userbyid(members, fst).name        

        await self.send("Choose your delusions with /choose <id>'")
        await self.slist(name1, snd, "dsmn")
        await self.slist(name0, fst, "dsmn")

        self.game['state'] = 'choosing'

    @commands.command(pass_context=True, name="choose")
    async def choose(self, ctx, dsmn):
        if ctx.message.author.id in self.game.values() and self.game['state'] == 'choosing': """"""
        else: return

        if not self.dbfun.hasdsmn(ctx.message.author.id, dsmn):
            await self.send("You didn't realboot this delusion.")
            return

        if self.game['plr1'] == ctx.message.author.id: self.game['dsmn1'] = dsmn
        if self.game['plr0'] == ctx.message.author.id: self.game['dsmn0'] = dsmn
        
        data = (self.game['dsmn1'], self.game['dsmn0'])
        if '' in data: return

        members = ctx.message.server.members

        snd = self.game['plr1']
        fst = self.game['plr0']

        usr1 = self.userbyid(members, snd)
        usr0 = self.userbyid(members, fst)

        name1 = usr1.name
        name0 = usr0.name        

        dsmn1 = self.game['dsmn1']
        dsmn0 = self.game['dsmn0']

        await self.send("You've chosen your delusions, now try realbooting their Di-Sword with /atk <id>")
        await self.slist(name1, dsmn1, "abt")
        await self.slist(name0, dsmn0, "abt")        
        self.game['state'] = 'running'

    @commands.command(pass_context=True, name="atk")
    async def atk(self, ctx, abt):
        if ctx.message.author.id in self.game.values() and self.game['state'] == 'running': """"""
        else: return

        dsmn1 = self.game['dsmn1']
        dsmn0 = self.game['dsmn0']

        try:
            anm = self.dbfun.anmbyid(abt)
        except:
            await self.send("You're not able to realboot this.")
            return

        if ctx.message.author.id == self.game['plr1']:
            if not self.dbfun.hasabt(dsmn1, abt):
                await self.send("You're not able to realboot this.")
                return
            self.game['anm1'] = anm
            self.game['aid1'] = abt
        if ctx.message.author.id == self.game['plr0']:
            if not self.dbfun.hasabt(dsmn0, abt):
                await self.send("You're not able to realboot this.")
                return
            self.game['anm0'] = anm
            self.game['aid0'] = abt

        data = (self.game['aid1'], self.game['aid0'])
        if '' in data: return

        atker = self.game['atker']        
        aid1 = self.game['aid1']
        aid0 = self.game['aid0']
        snd = self.game['plr1']
        fst = self.game['plr0']

        members = self.game['mbrs']
        id = self.game['atker']
        name = self.userbyid(members, id).name
        dst = self.game['dst']
        await self.send("Di-Swords are getting realbooted...", dst=dst)
        time.sleep(0.5)
        await self.send("***" + name + " is faster.***", dst=dst)
        dsmns = (dsmn0, dsmn1)

        if atker == snd:
            s = self.userbyid(members, fst)
            f = self.userbyid(members, snd)
            sanm = self.game['anm0']
            fanm = self.game['anm1']
        if atker == fst:
            s = self.userbyid(members, snd)
            f = self.userbyid(members, fst)     
            sanm = self.game['anm1']            
            fanm = self.game['anm0']

        dname1 = self.dbfun.dnmbyid(dsmn1)
        dname0 = self.dbfun.dnmbyid(dsmn0)
        sname = s.name
        fname = f.name
        await self.send("***" + fname + "'s*** delusion starts using ***" + fanm + "*** on ***" + sname + "'s*** delusion", dst=dst)
        time.sleep(0.5)
        await self.send("***" + fname + "'s*** delusion is hit by ***" + sanm + "*** from ***" + sname + "'s*** delusion", dst=dst)        
        time.sleep(0.5)        
        info = await self.fight(dsmns[0], dsmns[1], aid0, aid1)
        time.sleep(0.5)
        await self.send("***And the winner is: *** " + info, dst=dst)
        self.game = {'state': 'nothing', 'aid1': '', 'aid0': '', 'anm1': '', 'anm0': '', 'atker': '', 'plr1': '', 'plr0': '', 'dsmn1': '', 'dsmn0': ''}

    @commands.command(pass_context=True, name="dlsn-gn")
    async def dsmngnr(self, ctx):
        if ctx.message.author.id != "127658424082104320": return

        mbrs = ctx.message.server.members

        self.dsmn = random.sample(list(mbrs), 1)[0]
        name = self.dsmn.name
        
        await self.send("*" + name + " is sensing a 'gaze'...*")

    @commands.command(pass_context=True, name="type-a")
    async def typea(self, ctx, *, flds):
        if ctx.message.author.id != "127658424082104320": return
        
        flds = flds.split(';')
        data = (flds[0], flds[1], flds[2])

        self.dbfun.insert(data, "type")

    @commands.command(pass_context=True, name="abt-a")
    async def abta(self, ctx, *, flds):
        if ctx.message.author.id != "127658424082104320": return
        
        flds = flds.split(';')
        data = (flds[0], flds[1], flds[2])

        self.dbfun.insert(data, "abt")

    @commands.command(pass_context=True, name="type-d")
    async def typed(self, ctx, id):
        if ctx.message.author.id != "127658424082104320": return
        
        self.dbfun.delete(id, "type")

    @commands.command(pass_context=True, name="abt-d")
    async def abtd(self, ctx, id):
        if ctx.message.author.id != "127658424082104320": return
        
        self.dbfun.delete(id, "abt")

    @commands.command(pass_context=True, name="type-i")
    async def typei(self, ctx, type : int):
        """Info on a type"""

        if not type in range(1, self.amo['type']+1):
            await self.send("Type isn't stored.")
            return

        info = self.info(type, "type")
        await self.send('', info)

    @commands.command(pass_context=True, name="dlsn-i")
    async def dsmni(self, ctx, dsmn):
        """Info on a delusion"""
        
        if not self.dbfun.hasdsmns(ctx.message.author.id):
            await self.send("You didn't realboot any delusions.")
            return

        if not self.dbfun.hasdsmn(ctx.message.author.id, dsmn):
            await self.send("You didn't realboot this delusion.")
            return

        info = self.info(dsmn, "dsmn")
        await self.send('', info)

    @commands.command(pass_context=True, name="dlsn-f")
    async def dsmnf(self, ctx, dsmn):
        """Free a delusion"""

        if not self.dbfun.hasdsmns(ctx.message.author.id):
            await self.send("You didn't realboot any delusions.")
            return

        if not self.dbfun.hasdsmn(ctx.message.author.id, dsmn):
            await self.send("You didn't realboot this delusion.")
            return
        
        self.dbfun.free(dsmn)
        await self.send("Delusion was freed.")

        r = random.randint(0, 10)
        if r < 7: return
        mbrs = ctx.message.server.members
        self.dsmn = random.sample(list(mbrs), 1)[0]
        name = self.dsmn.name
        
        await self.send(name + " is sensing a 'gaze'...")

    @commands.command(pass_context=True, name="dlsn-n")
    async def dsmnn(self, ctx, dsmn, name):
        """Name a delusion"""
        
        if not self.dbfun.hasdsmns(ctx.message.author.id):
            await self.send("You didn't realboot any delusions.")
            return

        if not self.dbfun.hasdsmn(ctx.message.author.id, dsmn):
            await self.send("You didn't realboot this delusion.")
            return
            
        self.dbfun.name(dsmn, name)
        await self.send("Delusion was renamed.")

    @commands.command(pass_context=True, name="try-t")
    async def trytr(self, ctx, name, dsmn):
        """Try trading with someone"""

        if ctx.message.author.id in name or ctx.message.raw_mentions == []: return

        if not self.dbfun.hasdsmns(ctx.message.author.id):
            await self.send("You didn't realboot any delusions.")
            return

        if not self.dbfun.hasdsmn(ctx.message.author.id, dsmn):
            await self.send("You didn't realboot this delusion.")
            return

        await self.send("Accept the request with /acpt-t <dlsn id>")

        self.trd['state'] = "running"
        self.trd['dsmn1'] = dsmn
        mbrs = ctx.message.server.members
        id = ctx.message.raw_mentions[0]
        self.trd['otr'] = self.userbyid(mbrs, id)

    @commands.command(pass_context=True, name="dlsn-g")
    async def dsmng(self, ctx, name, dsmn):
        """Give a delusion to someone"""

        if ctx.message.author.id in name or ctx.message.raw_mentions == []: return
        
        if not self.dbfun.hasdsmns(ctx.message.author.id):
            await self.send("You didn't realboot any delusions.")
            return

        if not self.dbfun.hasdsmn(ctx.message.author.id, dsmn):
            await self.send("You didn't realboot this delusion.")
            return
        
        mbrs = ctx.message.server.members
        id = ctx.message.raw_mentions[0]
        self.dbfun.cmstr(dsmn, id)
        await self.send("Delusion handed over successfully.")

    @commands.command(pass_context=True, name="acpt-t")
    async def acptt(self, ctx, dsmn):
        """Accept the trade"""

        if self.trd['otr'] != ctx.message.author or self.trd['state'] != 'running': return

        if not self.dbfun.hasdsmns(ctx.message.author.id):
            await self.send("You didn't realboot any delusions, trade has been cancelled.")
            self.trd['state'] = 'nothing'
            return

        if not self.dbfun.hasdsmn(ctx.message.author.id, dsmn):
            await self.send("You didn't realboot this delusion.")
            return

        await self.send("Trading was successful.")        

        self.trd['dsmn0'] = dsmn
        dsmn1 = self.trd['dsmn1']
        dsmn0 = self.trd['dsmn0']        

        self.dbfun.switch(dsmn1, dsmn0)

    @commands.command(pass_context=True, name="dlsn-a")
    async def dsmna(self, ctx, dsmn):
        """Show abilities of delusions"""

        if not self.dbfun.hasdsmns(ctx.message.author.id):
            await self.send("You didn't realboot any delusions.")
            return

        if not self.dbfun.hasdsmn(ctx.message.author.id, dsmn):
            await self.send("You didn't realboot this delusion.")
            return

        if not self.dbfun.hasabts(dsmn): return

        name = ctx.message.author.name
        await self.slist(name, dsmn, "abt")

    @commands.command(pass_context=True, name="dlsn-l")
    async def dsmnl(self, ctx):
        """Show your delusions"""
        
        if not self.dbfun.hasdsmns(ctx.message.author.id):
            await self.send("You didn't realboot any delusions.")
            return
        user = ctx.message.author
        name = user.name
        id = user.id
        await self.slist(name, id, "dsmn")

def setup(bot):
    bot.add_cog(Dsmn(bot))
