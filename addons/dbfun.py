import discord
import random
import sqlite3
import time
from datetime import datetime
from discord.ext import commands
from random import randint

class DBFun(object):
    """
    DBFun
    """

    # Construct
    def __init__(self, bot):
        self.bot = bot

    def hasabt(self, dsmn, abt):
        self.bot.cursor.execute("SELECT * FROM arow JOIN abt ON arow.abt_id = abt.rowid WHERE arow.dsmn_id = ? AND abt.rowid = ?", (dsmn, abt))
        if len(self.bot.cursor.fetchall()) > 0: return True
        return False

    def hasdsmn(self, user, dsmn):
        for row in self.dsmnsids(user):
            if dsmn == str(row[0]):
                return True
        return False

    def hasdsmns(self, id):
        self.bot.cursor.execute("SELECT rowid FROM dsmn WHERE master = ?", (id,))
        if len(self.bot.cursor.fetchall()) > 0: return True
        else: return False

    def updsts(self, dsmn, lvl, exp):
        data = (exp, lvl, dsmn)
        self.bot.cursor.execute("UPDATE dsmn SET exp = ?, level = ? WHERE rowid = ?", data)
        self.bot.db.commit()

    def listbase(self, id, tab):
        if tab == "abt": self.bot.cursor.execute("SELECT abt_id, level, name FROM arow JOIN abt ON arow.abt_id = abt.rowid WHERE arow.dsmn_id = " + str(id))
        if tab == "dsmn": self.bot.cursor.execute("SELECT rowid, level, nick FROM dsmn WHERE master = ?", (id,))
        return self.bot.cursor.fetchall()        

    def infobase(self, id, tab):
        if tab == "dsmn": self.bot.cursor.execute("SELECT nick, name, avatar, roles, exp, level, born, type_id FROM dsmn WHERE rowid = ?", (id,))
        if tab == "type": self.bot.cursor.execute("SELECT levelupstep, name, info FROM type WHERE rowid = ?", (id,))        
        return self.bot.cursor.fetchone()

    def expbase(self, dsmn):
        self.bot.cursor.execute("SELECT levelupstep, level, exp, nick FROM type JOIN dsmn ON dsmn.type_id = type.rowid WHERE dsmn.rowid = ?", (dsmn,))
        return self.bot.cursor.fetchone()

    def fgtbase(self, d1, d0, a1, a0):
        print("SELECT dsmn.exp, dsmn.rowid, abt.level, dsmn.nick, abt.rowid, abt.info FROM dsmn JOIN arow ON arow.dsmn_id = dsmn.rowid JOIN abt ON arow.abt_id = abt.rowid JOIN type ON dsmn.type_id = type.rowid WHERE (arow.dsmn_id = " + d1 + " AND arow.abt_id = " + a1 + ") OR (arow.dsmn_id = " + d0 + " AND arow.abt_id = " + a0 + ")")
        self.bot.cursor.execute("SELECT dsmn.exp, dsmn.rowid, abt.level, dsmn.nick, abt.rowid, abt.info FROM dsmn JOIN arow ON arow.dsmn_id = dsmn.rowid JOIN abt ON arow.abt_id = abt.rowid JOIN type ON dsmn.type_id = type.rowid WHERE (arow.dsmn_id = ? AND arow.abt_id = ?) OR (arow.dsmn_id = ? AND arow.abt_id = ?)", (d1, a1, d0, a0))
        return self.bot.cursor.fetchall()

    def anmbyid(self, id):
        self.bot.cursor.execute("SELECT name FROM abt WHERE rowid = ?", (id,))
        return self.bot.cursor.fetchone()[0]

    def dnmbyid(self, id):
        self.bot.cursor.execute("SELECT nick FROM dsmn WHERE rowid = ?", (id,))
        return self.bot.cursor.fetchone()[0]

    def dsmnsids(self, id):
        self.bot.cursor.execute("SELECT rowid FROM dsmn WHERE master = ?", (id,))
        return self.bot.cursor.fetchall()

    def hasabts(self, dsmn):
        self.bot.cursor.execute("SELECT * FROM arow JOIN abt ON arow.abt_id = abt.rowid WHERE arow.dsmn_id = ?", (dsmn,))
        if len(self.bot.cursor.fetchall()) > 0: return True
        return False

    def free(self, id):
        self.bot.cursor.execute("UPDATE dsmn SET master = '' WHERE rowid = ?", (id,))
        self.bot.db.commit()

    def switch(self, id1, id0):
        self.bot.cursor.execute("SELECT master FROM dsmn WHERE rowid = ?", (id1,))
        mid1 = self.bot.cursor.fetchone()[0]
        self.bot.cursor.execute("SELECT master FROM dsmn WHERE rowid = ?", (id0,))
        mid0 = self.bot.cursor.fetchone()[0]
        self.bot.cursor.execute("UPDATE dsmn SET master = ? WHERE rowid = ?", (mid1, id0))
        self.bot.db.commit()        
        self.bot.cursor.execute("UPDATE dsmn SET master = ? WHERE rowid = ?", (mid0, id1))
        self.bot.db.commit()

    def cmstr(self, dsmn, id):
        self.bot.cursor.execute("UPDATE dsmn SET master = ? WHERE rowid = ?", (id, dsmn))
        self.bot.db.commit()

    def insert(self, vals, tab):
        if tab == "type": self.bot.cursor.execute("INSERT INTO type VALUES(?,?,?)", vals)
        if tab == "dsmn": self.bot.cursor.execute("INSERT INTO dsmn VALUES(?,?,?,?,?,?,?,?,?,?,?,?)", vals)
        if tab == "arow": self.bot.cursor.execute("INSERT INTO arow VALUES(?,?)", vals)
        if tab == "abt": self.bot.cursor.execute("INSERT INTO abt VALUES(?,?,?)", vals)
        self.bot.db.commit()

    def lnabt(self, dsmn, id1, id0):
        self.bot.cursor.execute("UPDATE arow SET abt_id = ? WHERE dsmn_id = ? AND abt_id = ?", (id1, dsmn, id0))
        self.bot.db.commit()

    def amo(self, tab):
        if tab == "type": self.bot.cursor.execute("SELECT * FROM type")
        if tab == "dsmn": self.bot.cursor.execute("SELECT * FROM dsmn")
        if tab == "abt": self.bot.cursor.execute("SELECT * FROM abt")
        if tab == "arow": self.bot.cursor.execute("SELECT * FROM arow")
        return len(self.bot.cursor.fetchall())

    def name(self, dsmn, name):
        self.bot.cursor.execute("UPDATE dsmn SET nick = ? WHERE rowid = ?", (name, dsmn))
        self.bot.db.commit()

    def delete(self, id, tab):
        if tab == "type": self.bot.cursor.execute("DELETE FROM type WHERE rowid = ?", (id,))
        if tab == "abt": self.bot.cursor.execute("DELETE FROM abt WHERE rowid = ?", (id,))        
        self.bot.db.commit()
