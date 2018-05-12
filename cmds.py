import json
import discord
import Go
from Go import *

prefix = "4."


def readjson(path):
    with open(path) as fil:
        return json.load(fil)


def isupdate(msg):
    return msg.content == prefix + "update" and msg.author.id in (212350439532789760, 136611352692129792)


def isowner(msg):
    return msg.author.id in (212350439532789760, 136611352692129792)


# Below is the code that runs every time a message is sent, handles commands
async def process(msg, client):
    print(msg.content)
    if msg.content[:len(prefix)] == prefix:
        arr = msg.content[len(prefix):].split(" ")
        # Arr is short for argument. Milo's idea for coding commands
        if arr[0] == "help":
            await msg.channel.send("```4.help: pulls up this menu \n"
                                   "4.go create @player: creates a game with you and player```")
        if arr[0] == "update" and isowner(msg):
            await msg.channel.send("Updated")
        if arr[0] == "go":
            if arr[1] == "create":
                game = GoGame(5)
                await msg.channel.send("```" + game.printboard(game.board) + "```")
