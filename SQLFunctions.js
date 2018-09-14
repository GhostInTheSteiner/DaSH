var Discord = require("discord.js");
var bot = new Discord.Client();
var sqlite3 = require("sqlite3")
var db = new sqlite3.Database("chat.db");
var d1 = new sqlite3.Database("chat.db", sqlite3.OPEN_READONLY);
var Table = require('cli-table2');

var channelExceptions = `'robotulismusic', 'bot', 'dmc', 'sciadv-general-discussion', 'sciadv-series', 'occultic-fine', 'chaos-chives', 'chaos-child-anime-channel', 'chaoscontrol', 'chaos-control', 'chaos-control-anime', 'sg-zero-discussion', 'chaos-series-discussion', 'svn-discussion', 'robotics-notes-discussion', 'robotics-matter-dash-discussion'`

bot.on("message", msg => {
    if(msg.content.startsWith("/sql") && !msg.content.startsWith("/sql-h")) {
        try {
        d1.all(msg.content.substring(5), {}, (err, rows) => {
            writeResuslt(err, rows, msg);
        });
        } catch (f) {
            msg.channel.sendMessage("nope");
        }
    }
});

bot.on("message", msg => {
    if (msg.content.startsWith("/hist")) {
        try {
            var h = msg.content.split(" ")[2];
            var m = msg.content.split(" ")[1];
            switch (msg.content.split(" ")[0]) {
                case "/hist-a": var txt = "SELECT strftime('%d-%m-%Y', time) day, round(count(1) * 100/" + h + ") [%] FROM dis WHERE datetime(time) > datetime(\'now\', \'-" + m + " day\') AND server_ID = \'" + msg.channel.guild.id + "\' GROUP BY day ORDER BY time desc";
                                break;
                case "/hist-r": var txt = "WITH v(amo) AS (SELECT avg(h) FROM (SELECT count(1) h FROM dis WHERE datetime(time) > datetime(\'now\', \'-" + m + " day\') AND server_ID = \'" + msg.channel.guild.id + "\' GROUP BY strftime('%d %m %Y', time)) h) SELECT strftime('%d-%m-%Y', time) day, round(count(1) * 100/v.amo) [%] FROM v, dis WHERE datetime(time) > datetime(\'now\', \'-" + m + " day\') AND server_ID = \'" + msg.channel.guild.id + "\' GROUP BY day ORDER BY time desc";
                                break;
                case "/hist": var txt = "SELECT strftime(\'%d-%m-%Y %H:00\', time) UTC0, count(1) n FROM dis WHERE datetime(time) > datetime(\'now\', \'-" + m + " hour\') AND server_ID = \'" + msg.channel.guild.id + "\' GROUP BY UTC0 ORDER BY UTC0 desc";
                              break;
                case "/hist-h": var txt = "SELECT strftime(\'%H\', time) hour, count(1) n FROM dis WHERE datetime(time) > datetime(\'now\', \'-" + m + " hour\') AND server_ID = \'" + msg.channel.guild.id + "\' GROUP BY hour ORDER BY hour desc";
                                break;
                case "/hist-w": var txt = "SELECT strftime(\'%Y %W\', time) week, count(1) n FROM dis WHERE datetime(time) > datetime(\'now\', \'-" + m*7 + " day\') AND server_ID = \'" + msg.channel.guild.id + "\' GROUP BY week ORDER BY week desc";
                                break;
                case "/hist-d": var txt = "SELECT strftime(\'%d-%m-%Y\', time) day, count(1) n FROM dis WHERE datetime(time) > datetime(\'now\', \'-" + m + " day\') AND server_ID = \'" + msg.channel.guild.id + "\' GROUP BY day ORDER BY day desc";
                                break;
            }
            d1.all(txt, {}, (err, rows) => {
                writeResuslt(err, rows, msg);
            });
        } catch (f) {
            msg.channel.sendMessage("nope");
            return;
        }
    }

    if (msg.content.startsWith("/find")) {
        try {
            var words = msg.content.substring(msg.content.indexOf(" ", 8) + 1);
            var limit = msg.content.split(" ")[1];
            switch (msg.content.split(" ")[0]) {
                case "/find": var txt = "SELECT content, name FROM dis WHERE content LIKE \'%" + msg.content.substring(6) + "%\' AND channel NOT IN(" + channelExceptions + ") AND channel NOT LIKE \'%spoil%\' AND channel NOT LIKE \'%nsfw%\' AND channel NOT LIKE \'%hentai%\' ORDER BY time desc limit 1";
                              break;
                case "/find-l": var txt = "SELECT content, name FROM dis WHERE content LIKE \'%" + words + "%\' AND channel NOT IN(" + channelExceptions + ") AND channel NOT LIKE \'%spoil%\' AND channel NOT LIKE \'%nsfw%\' AND channel NOT LIKE \'%hentai%\' ORDER BY time desc limit " + limit;
                                break;
                case "/find-u": var txt = "SELECT content, name FROM dis WHERE name LIKE \'%" + words + "%\' AND channel NOT IN(" + channelExceptions + ") AND channel NOT LIKE \'%spoil%\' AND channel NOT LIKE \'%nsfw%\' AND channel NOT LIKE \'%hentai%\' ORDER BY time desc limit " + limit;
                                break;
            }
            d1.all(txt, {}, (err, rows) => {
                getMsg(err, rows, msg);
            });
        } catch (f) {
            msg.channel.sendMessage("nope");
            return;
        }
    }

    if (msg.content.startsWith("/ran")) {
        try {
            var m = msg.content.substring(7);
            switch (msg.content.split(" ")[0]) {
                case "/ran-w": var txt = "SELECT content, name FROM dis WHERE content LIKE \'%" + m + "%\' AND channel NOT IN(" + channelExceptions + ") AND channel NOT LIKE \'%spoil%\' AND channel NOT LIKE \'%nsfw%\' AND channel NOT LIKE \'%hentai%\' ORDER BY random() limit 1";
                               break;
                case "/ran-u": var txt = "SELECT content, name FROM dis WHERE name like \'" + m + "\' AND channel NOT IN(" + channelExceptions + ") AND channel NOT LIKE \'%spoil%\' AND channel NOT LIKE \'%nsfw%\' AND channel NOT LIKE \'%hentai%\' ORDER BY random() limit 1";
                               break;
                case "/ran": var txt = "SELECT content, name FROM dis WHERE channel NOT IN(" + channelExceptions + ") AND channel NOT LIKE \'%spoil%\' AND channel NOT LIKE \'%nsfw%\' AND channel NOT LIKE \'%hentai%\' ORDER BY random() limit 1";
                             break;
            }
            d1.all(txt, {}, (err, rows) => {
                getMsg(err, rows, msg);
            });
        } catch (f) {
            msg.channel.sendMessage("nope");
            return;
        }
    }
});

bot.on("message", msg => {
    if(msg.content == "/sql-h") {
        msg.channel.sendMessage("**SQL for Discord!** This aims to be a feature to support data mining chats. You don't need to be a coding nerd to use it (\'_v\')\n\nHere are some examples:\n\n**SELECT** name **FROM** dis **WHERE** content = 'lol' limit 5 \t*lists everyone who posted lol*\n**SELECT** content **FROdM** dis **WHERE** channel = 'general' limit 5 \t*messages posted in general*\n**SELECT** * **FROM** dis limit 5 \t*first rows of dis*\n\n**columns = {server, name, nick, content, time, channel} table = \"dis\"**\n\nSyntax:\n\nSELECT [columns]\n\FROM [table]\nWHERE [condition]")
    }
});

function writeResuslt(err, rows, msg) {
    if (err || rows[0] == undefined) {
        msg.channel.sendMessage(err);
        return;
    }
    rows = rows.slice(0, 100);
    table = tableFac(rows);
    rows.forEach((value, index, rows) => {
        var res = [];
        for (var key in value) {
            if (value[key] !== undefined) res.push(value[key]);
        }
        table.push(res);
    });
    msg.channel.sendMessage("```" + table.toString() + "```");
}

function getMsg(err, rows, msg) {
    if (err || rows[0] == undefined) {
        msg.channel.sendMessage(err);
        return;
    }
    rows = rows.slice(0, 10);
    rows.forEach((value, index, rows) => {
        msg.channel.sendMessage(value.name + ": " + value.content.replace("http://", "").replace("https://", ""));
    })
}

function tableFac(rows) {
    return new Table({
                        head: Object.keys(rows[0]),
                        style: {
                            head: [],
                            border: []
                        }
                    });
}

function fix(d) {
    return (d < 10) ? '0' + d.toString() : d;
}

bot.on('ready', () => {
    console.log('I am ready!');
});

bot.login("Sono me, dare no me?");