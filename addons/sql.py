import random
from discord.ext import commands


class Sql:

    class Markov(object):

        def __init__(self, open_db, field="", val="", tags=""):

            print("Markov Init")

            self.fail = False
            self.cache = {}
            self.words = []
            self.open_db = open_db

            tags = tags.split()

            if field == "" and val == "" and tags == []:
                self.open_db.execute("SELECT content FROM dis")
            elif field == "name" and val != "" and tags == []:
                self.open_db.execute("SELECT content FROM dis WHERE name like ?", (val,))
            elif field == "channel" and val != "" and tags == []:
                self.open_db.execute("SELECT content FROM dis WHERE channel like ?", (val,))
            else:
                self.similar(tags)

            print("Markov fetch")

            rows = open_db.fetchall()

            if len(rows) == 0:
                self.fail = True
                return

            for row in rows:
                self.words.extend(row[0].split())

            self.word_size = len(self.words)
            self.database()

        def similar(self, tags):

            print("Markov similar")

            obj = []
            for word in tags:
                obj.append(word)

            val1 = "%" + obj[random.randint(0, len(obj)-1)] + "%"
            val2 = "%" + obj[random.randint(0, len(obj)-1)] + "%"
            val3 = "%" + obj[random.randint(0, len(obj)-1)] + "%"
            val4 = "%" + obj[random.randint(0, len(obj)-1)] + "%"
            data = (val1, val2, val3, val4)

            self.open_db.execute("SELECT content FROM dis WHERE content like ? OR content like ? OR content like ? OR content like ?", data)

        def triples(self):

            print("Markov Triples")

            if len(self.words) < 3:
                return

            for i in range(len(self.words) - 2):
                yield (self.words[i], self.words[i+1], self.words[i+2])

        def database(self):

            print("Markov Database")

            for w1, w2, w3 in self.triples():
                key = (w1, w2)

                if key in self.cache:
                    self.cache[key].append(w3)
                else:
                    self.cache[key] = [w3]

        def generate_markov_text(self, size=25):

            print("Markov Generate Markov Text")

            seed = random.randint(0, self.word_size-3)
            seed_word, next_word = self.words[seed], self.words[seed+1]
            w1, w2 = seed_word, next_word
            gen_words = []

            for i in range(size):
                gen_words.append(w1)
                w1, w2 = w2, random.choice(self.cache[(w1, w2)])

            gen_words.append(w2)

            return ' '.join(gen_words)

    # Construct
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    # Send message
    async def send(self, msg):
        await self.bot.say(msg)

    # Commands
    @commands.command(pass_context=True, name="log-c")
    async def log_c(self, ctx, content: str):

        markov = self.Markov(self.bot.cursor, "channel", "%" + content + "%")

        if markov.fail:
            return

        await self.bot.send_message(ctx.message.channel, markov.generate_markov_text(14).replace("http://", "").replace("https://", ""))

    @commands.command(pass_context=True, name="log-u")
    async def log_u(self, ctx, content: str):

        markov = self.Markov(self.bot.cursor, "name", "%" + content + "%")

        if markov.fail:
            return

        await self.bot.send_message(ctx.message.channel, markov.generate_markov_text(14).replace("http://", "").replace("https://", ""))

    @commands.command(pass_context=True, name="log-s")
    async def log_s(self, ctx, content: str):

        markov = self.Markov(self.bot.cursor, "", "", content)

        if markov.fail:
            return

        await self.bot.send_message(ctx.message.channel, markov.generate_markov_text(14).replace("http://", "").replace("https://", ""))

    @commands.command(pass_context=True, name="log")
    async def log(self, ctx):

        markov = self.Markov(self.bot.cursor)

        if markov.fail:
            return

        await self.bot.send_message(ctx.message.channel, markov.generate_markov_text(14).replace("http://", "").replace("https://", ""))

def setup(bot):
    bot.add_cog(Sql(bot))
