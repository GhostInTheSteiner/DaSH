var exec = require('child_process').exec;
var Discord = require("discord.js");
var bot = new Discord.Client();
var child;

bot.on('message', msg => {
    if(msg.content.startsWith("/exec") && msg.author.id == "127658424082104320") run(msg.content.substring(6), msg);
});

function run(command, msg) {
    child = exec(command, (error, stdout, stderr) => {
        msg.channel.sendMessage("```" + stdout.slice(0, 1990) + "```");
        if (stderr !== "") {
            msg.channel.sendMessage("```" + stderr.slice(0, 2000) + "```");
        }
    });
}

bot.on('ready', () => {
    console.log('I am ready!');
});

bot.login("Sono me, dare no me?");